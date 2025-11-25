import logging
import shutil
import uuid
import os
import asyncio
from pathlib import Path
from typing import Optional, List
import psutil
import time

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from pdf2zh_next.config import ConfigManager
from pdf2zh_next.config.cli_env_model import CLIEnvSettingsModel
from pdf2zh_next.high_level import do_translate_async_stream
from pdf2zh_next.const import DEFAULT_CONFIG_DIR

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for tasks (in-memory for simplicity)
tasks = {}

class TranslationRequest(BaseModel):
    file_id: str
    lang_from: str
    lang_to: str
    service: str
    # Add other fields as needed

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        logger.info(f"Uploading file: {file.filename} (file_id: {file_id})")
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File uploaded successfully: {file_path.name} (size: {file_path.stat().st_size} bytes)")
        return {"file_id": file_id, "filename": file.filename, "path": str(file_path)}
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/translate")
async def start_translation(
    request: Request,
    file_id: str = Form(...),
    lang_from: str = Form(...),
    lang_to: str = Form(...),
    service: str = Form(...),
    # background_tasks: BackgroundTasks = None # No longer using background_tasks for this
):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "logs": []}
    logger.info(f"Task {task_id}: Created translation task for file_id {file_id}")
    
    # Find file
    files = list(UPLOAD_DIR.glob(f"{file_id}_*"))
    if not files:
        logger.warning(f"Task {task_id}: File not found for file_id {file_id}")
        raise HTTPException(status_code=404, detail="File not found")
    file_path = files[0]
    logger.info(f"Task {task_id}: Found file {file_path.name}")

    # Start task using asyncio.create_task instead of BackgroundTasks
    # This allows us to store the task object
    # Prepare UI inputs
    form_data = await request.form()
    ui_inputs = dict(form_data)
    
    # Ensure required fields are present (they should be from args, but good to have in dict)
    ui_inputs.update({
        "file_id": file_id,
        "lang_from": lang_from,
        "lang_to": lang_to,
        "service": service
    })

    task = asyncio.create_task(run_translation(task_id, file_path, ui_inputs))
    tasks[task_id] = {
        "status": "pending",
        "file_id": file_id,
        "lang_from": lang_from,
        "lang_to": lang_to,
        "service": service,
        "logs": [],
        "created_at": time.time(),
        "task_object": task
    }    
    return {"task_id": task_id}

@app.post("/api/cancel/{task_id}")
async def cancel_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = tasks[task_id]
    if task_info["status"] in ["completed", "failed", "cancelled"]:
        return {"status": task_info["status"], "message": "Task already finished"}
    
    if "task_object" in task_info:
        task_obj = task_info["task_object"]
        if not task_obj.done():
            task_obj.cancel()
            logger.info(f"Task {task_id}: Cancel requested")
            task_info["status"] = "cancelled"
            task_info["logs"].append("Task cancelled by user")
            return {"status": "cancelled"}
    
    return {"status": task_info.get("status", "unknown"), "message": "Could not cancel task"}

# ... (imports)
from pdf2zh_next.config.model import SettingsModel
from pdf2zh_next.config.translate_engine_model import (
    GUI_PASSWORD_FIELDS,
    GUI_SENSITIVE_FIELDS,
    TERM_EXTRACTION_ENGINE_METADATA,
    TERM_EXTRACTION_ENGINE_METADATA_MAP,
    TRANSLATION_ENGINE_METADATA,
    TRANSLATION_ENGINE_METADATA_MAP,
)
from pdf2zh_next.i18n import gettext as _
from string import Template
import typing

# Initialize config manager
config_manager = ConfigManager()

# ... (imports)
import requests
import cgi
import tempfile
import csv
import io
import chardet
from enum import Enum

class SaveMode(Enum):
    """Enum for configuration save behavior."""
    follow_settings = "follow_settings"
    never = "never"
    always = "always"

# Complete language map (copied from gui.py to avoid importing gradio)
lang_map = {
    "English": "en",
    "Simplified Chinese": "zh-CN",
    "Traditional Chinese - Hong Kong": "zh-HK",
    "Traditional Chinese - Taiwan": "zh-TW",
    "Japanese": "ja",
    "Korean": "ko",
    "Polish": "pl",
    "Russian": "ru",
    "Spanish": "es",
    "Portuguese": "pt",
    "Brazilian Portuguese": "pt-BR",
    "French": "fr",
    "Malay": "ms",
    "Indonesian": "id",
    "Turkmen": "tk",
    "Filipino (Tagalog)": "tl",
    "Vietnamese": "vi",
    "Kazakh (Latin)": "kk",
    "German": "de",
    "Dutch": "nl",
    "Irish": "ga",
    "Italian": "it",
    "Greek": "el",
    "Swedish": "sv",
    "Danish": "da",
    "Norwegian": "no",
    "Icelandic": "is",
    "Finnish": "fi",
    "Ukrainian": "uk",
    "Czech": "cs",
    "Romanian": "ro",
    "Hungarian": "hu",
    "Slovak": "sk",
    "Croatian": "hr",
    "Estonian": "et",
    "Latvian": "lv",
    "Lithuanian": "lt",
    "Belarusian": "be",
    "Macedonian": "mk",
    "Albanian": "sq",
    "Serbian (Cyrillic)": "sr",
    "Slovenian": "sl",
    "Catalan": "ca",
    "Bulgarian": "bg",
    "Maltese": "mt",
    "Swahili": "sw",
    "Amharic": "am",
    "Oromo": "om",
    "Tigrinya": "ti",
    "Haitian Creole": "ht",
    "Latin": "la",
    "Lao": "lo",
    "Malayalam": "ml",
    "Gujarati": "gu",
    "Thai": "th",
    "Burmese": "my",
    "Tamil": "ta",
    "Telugu": "te",
    "Oriya": "or",
    "Armenian": "hy",
    "Mongolian (Cyrillic)": "mn",
    "Georgian": "ka",
    "Khmer": "km",
    "Bosnian": "bs",
    "Luxembourgish": "lb",
    "Romansh": "rm",
    "Turkish": "tr",
    "Sinhala": "si",
    "Uzbek": "uz",
    "Kyrgyz": "ky",
    "Tajik": "tg",
    "Abkhazian": "ab",
    "Afar": "aa",
    "Afrikaans": "af",
    "Akan": "ak",
    "Aragonese": "an",
    "Avaric": "av",
    "Ewe": "ee",
    "Aymara": "ay",
    "Ojibwa": "oj",
    "Occitan": "oc",
    "Ossetian": "os",
    "Pali": "pi",
    "Bashkir": "ba",
    "Basque": "eu",
    "Breton": "br",
    "Chamorro": "ch",
    "Chechen": "ce",
    "Chuvash": "cv",
    "Tswana": "tn",
    "Ndebele, South": "nr",
    "Ndonga": "ng",
    "Faroese": "fo",
    "Fijian": "fj",
    "Frisian, Western": "fy",
    "Ganda": "lg",
    "Kongo": "kg",
    "Kalaallisut": "kl",
    "Church Slavic": "cu",
    "Guarani": "gn",
    "Interlingua": "ia",
    "Herero": "hz",
    "Kikuyu": "ki",
    "Rundi": "rn",
    "Kinyarwanda": "rw",
    "Galician": "gl",
    "Kanuri": "kr",
    "Cornish": "kw",
    "Komi": "kv",
    "Xhosa": "xh",
    "Corsican": "co",
    "Cree": "cr",
    "Quechua": "qu",
    "Kurdish (Latin)": "ku",
    "Kuanyama": "kj",
    "Limburgan": "li",
    "Lingala": "ln",
    "Manx": "gv",
    "Malagasy": "mg",
    "Marshallese": "mh",
    "Maori": "mi",
    "Navajo": "nv",
    "Nauru": "na",
    "Nyanja": "ny",
    "Norwegian Nynorsk": "nn",
    "Sardinian": "sc",
    "Northern Sami": "se",
    "Samoan": "sm",
    "Sango": "sg",
    "Shona": "sn",
    "Esperanto": "eo",
    "Scottish Gaelic": "gd",
    "Somali": "so",
    "Southern Sotho": "st",
    "Tatar": "tt",
    "Tahitian": "ty",
    "Tongan": "to",
    "Twi": "tw",
    "Walloon": "wa",
    "Welsh": "cy",
    "Venda": "ve",
    "Volapük": "vo",
    "Interlingue": "ie",
    "Hiri Motu": "ho",
    "Igbo": "ig",
    "Ido": "io",
    "Inuktitut": "iu",
    "Inupiaq": "ik",
    "Sichuan Yi": "ii",
    "Yoruba": "yo",
    "Zhuang": "za",
    "Tsonga": "ts",
    "Zulu": "zu",
}

rev_lang_map = {v: k for k, v in lang_map.items()}

page_map = {
    "All": None,
    "First": [0],
    "First 5 pages": list(range(0, 5)),
    "Range": None,
}

def _validate_rate_limit_inputs(true_rate_limit_mode: str, **inputs) -> tuple[bool, str]:
    if true_rate_limit_mode == "RPM":
        rpm = inputs.get("rpm_input", 0)
        if not isinstance(rpm, int | float) or rpm <= 0:
            return False, "RPM must be a positive integer"
        if isinstance(rpm, float) and not rpm.is_integer():
            return False, "RPM must be a positive integer"
    elif true_rate_limit_mode == "Concurrent Threads":
        threads = inputs.get("concurrent_threads", 0)
        if not isinstance(threads, int | float) or threads <= 0:
            return False, "Concurrent threads must be a positive integer"
        if isinstance(threads, float) and not threads.is_integer():
            return False, "Concurrent threads must be a positive integer"
    elif true_rate_limit_mode == "Custom":
        qps = inputs.get("custom_qps", 0)
        pool_workers = inputs.get("custom_pool_workers")
        if not isinstance(qps, int | float) or qps <= 0:
            return False, "QPS must be a positive integer"
        if isinstance(qps, float) and not qps.is_integer():
            return False, "QPS must be a positive integer"
        if pool_workers is not None and (not isinstance(pool_workers, int | float) or pool_workers < 0):
            return False, "Pool workers must be a non-negative integer"
        if isinstance(pool_workers, float) and not pool_workers.is_integer():
            return False, "Pool workers must be a non-negative integer"
    return True, ""

def _calculate_rate_limit_params(rate_limit_mode: str, ui_inputs: dict, default_qps: int = 4) -> tuple[int, int | None]:
    is_valid, error_msg = _validate_rate_limit_inputs(true_rate_limit_mode=rate_limit_mode, **ui_inputs)
    if not is_valid:
        logger.warning(f"Rate limit validation failed: {error_msg}")
        raise ValueError(error_msg)

    if rate_limit_mode == "RPM":
        rpm: int = ui_inputs.get("rpm_input", 240)
        qps = max(1, rpm // 60)
        pool_workers = min(1000, qps * 10)
    elif rate_limit_mode == "Concurrent Threads":
        threads: int = ui_inputs.get("concurrent_threads_input", 40)
        pool_workers = min(1000, max(1, min(int(threads * 0.9), max(1, threads - 20))))
        qps = max(1, pool_workers)
    else:
        qps = ui_inputs.get("custom_qps_input", default_qps)
        pool_workers = ui_inputs.get("custom_pool_workers")
        qps = int(qps)
        pool_workers = int(pool_workers) if pool_workers and pool_workers > 0 else None

    return qps, pool_workers if pool_workers and pool_workers > 0 else None

def _build_translate_settings(
    base_settings: CLIEnvSettingsModel,
    file_path: Path,
    output_dir: Path,
    save_mode: SaveMode,
    ui_inputs: dict,
) -> SettingsModel:
    # Clone base settings to avoid modifying the original
    translate_settings = base_settings.clone()
    original_output = translate_settings.translation.output
    original_pages = translate_settings.pdf.pages
    original_gui_settings = base_settings.gui_settings

    # Extract UI values
    service = ui_inputs.get("service")
    lang_from = ui_inputs.get("lang_from")
    lang_to = ui_inputs.get("lang_to")
    page_range = ui_inputs.get("page_range")
    page_input = ui_inputs.get("page_input")
    prompt = ui_inputs.get("prompt")
    ignore_cache = ui_inputs.get("ignore_cache") or ui_inputs.get("ignoreCache")

    # PDF Output Options
    no_mono = ui_inputs.get("no_mono") or ui_inputs.get("noMono")
    no_dual = ui_inputs.get("no_dual") or ui_inputs.get("noDual")
    dual_translate_first = ui_inputs.get("dual_translate_first") or ui_inputs.get("dualTranslateFirst")
    use_alternating_pages_dual = ui_inputs.get("use_alternating_pages_dual") or ui_inputs.get("useAlternatingPagesDual")
    watermark_output_mode = ui_inputs.get("watermark_output_mode") or ui_inputs.get("watermarkOutputMode")

    # Rate Limit Options
    rate_limit_mode = ui_inputs.get("rate_limit_mode")
    # Direct QPS/Worker settings from frontend
    qps_input = ui_inputs.get("qps")
    pool_max_workers_input = ui_inputs.get("pool_max_workers") or ui_inputs.get("poolMaxWorkers")
    term_qps_input = ui_inputs.get("term_qps") or ui_inputs.get("termQps")
    term_pool_max_workers_input = ui_inputs.get("term_pool_max_workers") or ui_inputs.get("termPoolMaxWorkers")

    # Advanced Translation Options
    min_text_length = ui_inputs.get("min_text_length") or ui_inputs.get("minTextLength")
    rpc_doclayout = ui_inputs.get("rpc_doclayout")
    enable_auto_term_extraction = ui_inputs.get("enable_auto_term_extraction")
    primary_font_family = ui_inputs.get("primary_font_family")

    # Advanced PDF Options
    skip_clean = ui_inputs.get("skip_clean")
    disable_rich_text_translate = ui_inputs.get("disable_rich_text_translate")
    enhance_compatibility = ui_inputs.get("enhance_compatibility")
    split_short_lines = ui_inputs.get("split_short_lines")
    short_line_split_factor = ui_inputs.get("short_line_split_factor")
    translate_table_text = ui_inputs.get("translate_table_text") or ui_inputs.get("translateTableText")
    skip_scanned_detection = ui_inputs.get("skip_scanned_detection") or ui_inputs.get("skipScannedDetection")
    ocr_workaround = ui_inputs.get("ocr_workaround") or ui_inputs.get("ocrWorkaround")
    max_pages_per_part = ui_inputs.get("max_pages_per_part") or ui_inputs.get("maxPagesPerPart")
    formular_font_pattern = ui_inputs.get("formular_font_pattern")
    formular_char_pattern = ui_inputs.get("formular_char_pattern")
    auto_enable_ocr_workaround = ui_inputs.get("auto_enable_ocr_workaround") or ui_inputs.get("autoEnableOcrWorkaround")
    only_include_translated_page = ui_inputs.get("only_include_translated_page")

    # BabelDOC v0.5.1 new options
    merge_alternating_line_numbers = ui_inputs.get("merge_alternating_line_numbers")
    remove_non_formula_lines = ui_inputs.get("remove_non_formula_lines")
    non_formula_line_iou_threshold = ui_inputs.get("non_formula_line_iou_threshold")
    figure_table_protection_threshold = ui_inputs.get(
        "figure_table_protection_threshold"
    )
    skip_formula_offset_calculation = ui_inputs.get("skip_formula_offset_calculation")

    # Term extraction options
    term_service = ui_inputs.get("term_service")
    term_rate_limit_mode = ui_inputs.get("term_rate_limit_mode")
    term_rpm_input = ui_inputs.get("term_rpm_input")
    term_concurrent_threads = ui_inputs.get("term_concurrent_threads")
    term_custom_qps = ui_inputs.get("term_custom_qps")
    term_custom_pool_workers = ui_inputs.get("term_custom_pool_workers")

    # New input for custom_system_prompt
    custom_system_prompt_input = ui_inputs.get("custom_system_prompt_input") or ui_inputs.get("customSystemPrompt")
    glossaries = ui_inputs.get("glossaries")
    save_auto_extracted_glossary = ui_inputs.get("save_auto_extracted_glossary")

    # Map UI language selections to language codes
    source_lang = lang_map.get(lang_from, "auto")
    target_lang = lang_map.get(lang_to, "zh")

    # Set up page selection
    if page_range == "Range" and page_input:
        pages = page_input  # The backend parser handles the format
    else:
        # Use predefined ranges from page_map
        selected_pages = page_map[page_range]
        if selected_pages is None:
            pages = None  # All pages
        else:
            # Convert page indices to comma-separated string
            pages = ",".join(
                str(p + 1) for p in selected_pages
            )  # +1 because UI is 1-indexed

    # Update settings with UI values
    translate_settings.basic.input_files = {str(file_path)}
    translate_settings.report_interval = 0.2
    translate_settings.translation.lang_in = source_lang
    translate_settings.translation.lang_out = target_lang
    translate_settings.translation.output = str(output_dir)
    if ignore_cache is not None:
        translate_settings.translation.ignore_cache = ignore_cache

    # Update Translation Settings
    if min_text_length is not None:
        translate_settings.translation.min_text_length = int(min_text_length)
    if rpc_doclayout:
        translate_settings.translation.rpc_doclayout = rpc_doclayout

    # UI uses positive switch, config uses negative flag, so we invert here
    if enable_auto_term_extraction is not None:
        translate_settings.translation.no_auto_extract_glossary = (
            not enable_auto_term_extraction
        )
    if primary_font_family:
        if primary_font_family == "Auto":
            translate_settings.translation.primary_font_family = None
        else:
            translate_settings.translation.primary_font_family = primary_font_family

    # Rate Limit Options
    if rate_limit_mode:
        # Logic to handle rate limit mode if needed, or just pass it
        pass

    # Term extraction options
    if term_service:
        # Logic for term service
        pass

    translate_settings.basic.gui = False

    # Calculate and update rate limit settings
    if service != "SiliconFlowFree":
        if qps_input:
             qps = qps_input
             pool_workers = pool_max_workers_input
        else:
            qps, pool_workers = _calculate_rate_limit_params(
                rate_limit_mode, ui_inputs, translate_settings.translation.qps or 4
            )

        # Update translation settings
        translate_settings.translation.qps = int(qps)
        translate_settings.translation.pool_max_workers = (
            int(pool_workers) if pool_workers is not None else None
        )

    # Calculate and update term extraction rate limit settings
    if term_rate_limit_mode:
        term_rate_inputs = {
            "rpm_input": term_rpm_input,
            "concurrent_threads": term_concurrent_threads,
            "custom_qps": term_custom_qps,
            "custom_pool_workers": term_custom_pool_workers,
        }
        term_qps, term_pool_workers = _calculate_rate_limit_params(
            term_rate_limit_mode,
            term_rate_inputs,
            translate_settings.translation.term_qps
            or translate_settings.translation.qps
            or 4,
        )
        translate_settings.translation.term_qps = int(term_qps)
        translate_settings.translation.term_pool_max_workers = (
            int(term_pool_workers) if term_pool_workers is not None else None
        )

    # Reset all term extraction engine flags
    for term_metadata in TERM_EXTRACTION_ENGINE_METADATA:
        term_flag_name = f"term_{term_metadata.cli_flag_name}"
        if hasattr(translate_settings, term_flag_name):
            setattr(translate_settings, term_flag_name, False)

    # Configure term extraction engine settings from UI when not following main engine
    follow_main_label = _("Follow main translation engine")
    if (
        term_service
        and term_service != follow_main_label
        and not translate_settings.translation.no_auto_extract_glossary
        and term_service in TERM_EXTRACTION_ENGINE_METADATA_MAP
    ):
        term_metadata = TERM_EXTRACTION_ENGINE_METADATA_MAP[term_service]

        # Enable selected term extraction engine flag
        term_flag_name = f"term_{term_metadata.cli_flag_name}"
        if hasattr(translate_settings, term_flag_name):
            setattr(translate_settings, term_flag_name, True)

        # Update term extraction engine detail settings
        if term_metadata.cli_detail_field_name:
            term_detail_field_name = f"term_{term_metadata.cli_detail_field_name}"
            term_detail_settings = getattr(translate_settings, term_detail_field_name)
            term_model_type = term_metadata.term_setting_model_type

            for field_name, field in term_model_type.model_fields.items():
                if field_name in ("translate_engine_type", "support_llm"):
                    continue

                value = ui_inputs.get(field_name)
                if value is None:
                    continue

                type_hint = field.annotation
                original_type = typing.get_origin(type_hint)
                type_args = typing.get_args(type_hint)

                if type_hint is str or str in type_args:
                    pass
                elif type_hint is int or int in type_args:
                    value = int(value)
                elif type_hint is bool or bool in type_args:
                    value = bool(value)
                else:
                    raise Exception(
                        f"Unsupported type {type_hint} for field {field_name} in gui term extraction engine settings"
                    )

                setattr(term_detail_settings, field_name, value)

    # Update PDF Settings
    if no_mono is not None:
        translate_settings.pdf.no_mono = no_mono
    if no_dual is not None:
        translate_settings.pdf.no_dual = no_dual
    if dual_translate_first is not None:
        translate_settings.pdf.dual_translate_first = dual_translate_first
    if use_alternating_pages_dual is not None:
        translate_settings.pdf.use_alternating_pages_dual = use_alternating_pages_dual

    # Map watermark mode from UI to enum
    if watermark_output_mode:
        translate_settings.pdf.watermark_output_mode = (
            watermark_output_mode.lower().replace(" ", "_")
        )

    # Update Advanced PDF Settings
    if skip_clean is not None:
        translate_settings.pdf.skip_clean = skip_clean
    if disable_rich_text_translate is not None:
        translate_settings.pdf.disable_rich_text_translate = disable_rich_text_translate
    if enhance_compatibility is not None:
        translate_settings.pdf.enhance_compatibility = enhance_compatibility
    if split_short_lines is not None:
        translate_settings.pdf.split_short_lines = split_short_lines
    if ocr_workaround is not None:
        translate_settings.pdf.ocr_workaround = ocr_workaround
    if short_line_split_factor is not None:
        translate_settings.pdf.short_line_split_factor = float(short_line_split_factor)

    if translate_table_text is not None:
        translate_settings.pdf.translate_table_text = translate_table_text
    if skip_scanned_detection is not None:
        translate_settings.pdf.skip_scanned_detection = skip_scanned_detection
    if auto_enable_ocr_workaround is not None:
        translate_settings.pdf.auto_enable_ocr_workaround = auto_enable_ocr_workaround
    if only_include_translated_page is not None:
        translate_settings.pdf.only_include_translated_page = only_include_translated_page

    if max_pages_per_part is not None and max_pages_per_part > 0:
        translate_settings.pdf.max_pages_per_part = int(max_pages_per_part)

    if formular_font_pattern:
        translate_settings.pdf.formular_font_pattern = formular_font_pattern

    if formular_char_pattern:
        translate_settings.pdf.formular_char_pattern = formular_char_pattern

    # Apply BabelDOC v0.5.1 new options
    if merge_alternating_line_numbers is not None:
        translate_settings.pdf.no_merge_alternating_line_numbers = (
            not merge_alternating_line_numbers
        )
    if remove_non_formula_lines is not None:
        translate_settings.pdf.no_remove_non_formula_lines = not remove_non_formula_lines
    if non_formula_line_iou_threshold is not None:
        translate_settings.pdf.non_formula_line_iou_threshold = float(
            non_formula_line_iou_threshold
        )
    if figure_table_protection_threshold is not None:
        translate_settings.pdf.figure_table_protection_threshold = float(
            figure_table_protection_threshold
        )
    if skip_formula_offset_calculation is not None:
        translate_settings.pdf.skip_formula_offset_calculation = (
            skip_formula_offset_calculation
        )

    assert service in TRANSLATION_ENGINE_METADATA_MAP, "UNKNOW TRANSLATION ENGINE!"

    for metadata in TRANSLATION_ENGINE_METADATA:
        cli_flag = metadata.cli_flag_name
        setattr(translate_settings, cli_flag, False)

    metadata = TRANSLATION_ENGINE_METADATA_MAP[service]
    cli_flag = metadata.cli_flag_name
    setattr(translate_settings, cli_flag, True)
    if metadata.cli_detail_field_name:
        detail_setting = getattr(translate_settings, metadata.cli_detail_field_name)
        if metadata.setting_model_type:
            for field_name in metadata.setting_model_type.model_fields:
                if field_name == "translate_engine_type" or field_name == "support_llm":
                    continue
                
                # Fix: disable_gui_sensitive_input is not defined in this scope, get it from settings
                # disable_gui_sensitive_input = base_settings.gui_settings.disable_gui_sensitive_input
                
                # if disable_gui_sensitive_input:
                #     if field_name in GUI_PASSWORD_FIELDS:
                #         logger.warning(f"Skipping sensitive field {field_name} because disable_gui_sensitive_input is True")
                #         continue
                #     if field_name in GUI_SENSITIVE_FIELDS:
                #         logger.warning(f"Skipping sensitive field {field_name} because disable_gui_sensitive_input is True")
                #         continue
                value = ui_inputs.get(field_name)
                if value is None:
                    continue
                    
                type_hint = detail_setting.model_fields[field_name].annotation
                original_type = typing.get_origin(type_hint)
                type_args = typing.get_args(type_hint)
                if type_hint is str or str in type_args:
                    pass
                elif type_hint is int or int in type_args:
                    value = int(value)
                elif type_hint is bool or bool in type_args:
                    if isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        value = bool(value)
                else:
                    raise Exception(
                        f"Unsupported type {type_hint} for field {field_name} in gui translation engine settings"
                    )
                setattr(detail_setting, field_name, value)

    # Add custom prompt if provided
    if prompt:
        # This might need adjustment based on how prompt is handled in the new system
        translate_settings.custom_prompt = Template(prompt)

    # Add custom system prompt if provided
    if custom_system_prompt_input:
        translate_settings.translation.custom_system_prompt = custom_system_prompt_input
    else:
        translate_settings.translation.custom_system_prompt = None

    if glossaries:
        translate_settings.translation.glossaries = glossaries
    else:
        translate_settings.translation.glossaries = None

    if save_auto_extracted_glossary is not None:
        translate_settings.translation.save_auto_extracted_glossary = (
            save_auto_extracted_glossary
        )

    # Validate settings before proceeding
    try:
        translate_settings.validate_settings()
        temp_settings = translate_settings.to_settings_model()
        translate_settings.translation.output = original_output
        translate_settings.pdf.pages = original_pages
        translate_settings.gui_settings = original_gui_settings
        translate_settings.basic.gui = False
        translate_settings.basic.debug = False
        translate_settings.translation.glossaries = None

        # Determine if config should be saved based on save_mode
        should_save = False
        if save_mode == SaveMode.always:
            should_save = True
        elif save_mode == SaveMode.follow_settings:
            should_save = not temp_settings.gui_settings.disable_config_auto_save
        # SaveMode.never: should_save remains False

        if should_save:
            config_manager.write_user_default_config_file(settings=translate_settings)
            # global settings # Not using global settings variable here
            # settings = translate_settings
        temp_settings.validate_settings()
        return temp_settings
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid settings: {e}") from e




async def run_translation(task_id, file_path, ui_inputs):
    service = ui_inputs.get("service")
    lang_from = ui_inputs.get("lang_from")
    lang_to = ui_inputs.get("lang_to")
    translation_backend = ui_inputs.get("translationBackend", "stable")
    
    tasks[task_id]["status"] = "processing"
    logger.info(f"Task {task_id}: Starting translation for file {file_path.name}, from {lang_from} to {lang_to} using {service} (backend: {translation_backend})")
    
    try:
        if translation_backend == "stable":
            # Use stable pdf2zh backend
            await run_stable_translation(task_id, file_path, ui_inputs)
        else:
            # Use experimental pdf2zh_next backend
            await run_experimental_translation(task_id, file_path, ui_inputs)
    except asyncio.CancelledError:
        logger.info(f"Task {task_id}: Translation cancelled")
        tasks[task_id]["status"] = "cancelled"
        tasks[task_id]["logs"].append("Translation cancelled by user")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Task {task_id}: Translation failed: {error_msg}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = error_msg
        tasks[task_id]["logs"].append(f"Error: {error_msg}")


async def run_experimental_translation(task_id, file_path, ui_inputs):
    """Run translation using experimental pdf2zh_next backend"""
    # Load base settings
    config_manager = ConfigManager()
    base_settings = config_manager.initialize_cli_config()
    
    if "page_range" not in ui_inputs:
        ui_inputs["page_range"] = "All" # Default
    
    # Build settings
    settings = _build_translate_settings(
        base_settings,
        file_path,
        OUTPUT_DIR,
        SaveMode.never,
        ui_inputs
    )
    
    # Run translation
    mono_pdf_path = None
    dual_pdf_path = None
    async for event in do_translate_async_stream(settings, file_path):
        # Log the event
        if isinstance(event, dict):
            event_type = event.get("type")
            event_str = str(event)
            tasks[task_id]["logs"].append(event_str)
            logger.info(f"Task {task_id}: {event_str}")
            
            # Capture output file paths from finish event
            if event_type == "finish":
                result = event.get("translate_result")
                if result:
                    mono_pdf_path = result.mono_pdf_path
                    dual_pdf_path = result.dual_pdf_path
                    if mono_pdf_path:
                        tasks[task_id]["mono_pdf_path"] = str(mono_pdf_path)
                    if dual_pdf_path:
                        tasks[task_id]["dual_pdf_path"] = str(dual_pdf_path)
        else:
            event_str = str(event)
            tasks[task_id]["logs"].append(event_str)
            logger.info(f"Task {task_id}: {event_str}")
    
    tasks[task_id]["status"] = "completed"
    logger.info(f"Task {task_id}: Translation completed successfully (experimental backend)")
    
    # If we didn't capture paths from events, try to find them
    if not mono_pdf_path and not dual_pdf_path:
        # Look for files in OUTPUT_DIR matching the pattern
        pattern = f"{file_path.stem}*.pdf"
        matching_files = list(OUTPUT_DIR.glob(pattern))
        if matching_files:
            # Try to identify mono and dual files by name
            for pdf_file in matching_files:
                if ".mono." in pdf_file.name and not mono_pdf_path:
                    mono_pdf_path = pdf_file
                    tasks[task_id]["mono_pdf_path"] = str(mono_pdf_path)
                elif ".dual." in pdf_file.name and not dual_pdf_path:
                    dual_pdf_path = pdf_file
                    tasks[task_id]["dual_pdf_path"] = str(dual_pdf_path)
            
            # If still not found, use the most recent file as fallback
            if not mono_pdf_path and not dual_pdf_path:
                output_file = max(matching_files, key=lambda p: p.stat().st_mtime)
                tasks[task_id]["mono_pdf_path"] = str(output_file)


async def run_stable_translation(task_id, file_path, ui_inputs):
    """Run translation using stable pdf2zh backend"""
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    service = ui_inputs.get("service")
    lang_from = ui_inputs.get("lang_from")
    lang_to = ui_inputs.get("lang_to")
    page_range = ui_inputs.get("page_range", "All")
    page_input = ui_inputs.get("page_input", "")
    threads = ui_inputs.get("threads", 4)
    skip_subset_fonts = ui_inputs.get("skip_subset_fonts", False)
    ignore_cache = ui_inputs.get("ignoreCache", False)
    vfont = ui_inputs.get("vfont", "")
    prompt = ui_inputs.get("prompt", "")
    no_dual = ui_inputs.get("noDual", False)
    no_mono = ui_inputs.get("noMono", False)
    
    # Import pdf2zh components
    try:
        from pdf2zh.gui import translate as pdf2zh_translate
        # Try to import ModelInstance, but it's optional
        try:
            from pdf2zh.doclayout import ModelInstance
        except ImportError:
            ModelInstance = None
            logger.info("pdf2zh.doclayout.ModelInstance not available, continuing without it")
    except ImportError as e:
        logger.error(f"Task {task_id}: Failed to import pdf2zh: {e}")
        raise ImportError("pdf2zh is not installed. Please install it with: pip install pdf2zh") from e
    
    # Stable mode language map (pdf2zh uses different codes)
    stable_lang_map = {
        "English": "en",
        "Simplified Chinese": "zh",
        "Traditional Chinese": "zh-TW",
        "Traditional Chinese - Hong Kong": "zh-HK",
        "Traditional Chinese - Taiwan": "zh-TW",
        "Japanese": "ja",
        "Korean": "ko",
        "French": "fr",
        "German": "de",
        "Russian": "ru",
        "Spanish": "es",
        "Italian": "it",
        "Portuguese": "pt",
    }
    
    # Stable mode service map
    stable_service_map = {
        "Google": "Google",
        "Bing": "Bing",
        "DeepL": "DeepL",
        "DeepLX": "DeepLX",
        "Ollama": "Ollama",
        "Xinference": "Xinference",
        "AzureOpenAI": "AzureOpenAI",
        "OpenAI": "OpenAI",
        "Zhipu": "Zhipu",
        "ModelScope": "ModelScope",
        "SiliconFlow": "Silicon",
        "SiliconFlowFree": "Silicon",
        "Gemini": "Gemini",
        "Azure": "Azure",
        "TencentMechineTranslation": "Tencent",
        "Dify": "Dify",
        "AnythingLLM": "AnythingLLM",
        "Grok": "Grok",
        "Groq": "Groq",
        "DeepSeek": "DeepSeek",
        "OpenAICompatible": "OpenAI-liked",
        "QwenMt": "Ali Qwen-Translation",
    }
    
    # Stable mode page map
    stable_page_map = {
        "All": None,
        "First": [0],
        "First 5 pages": list(range(0, 5)),
        "Range": None,
    }
    
    # Prepare parameters
    source_lang = stable_lang_map.get(lang_from, "en")
    target_lang = stable_lang_map.get(lang_to, "zh")
    
    # Handle page selection
    if page_range == "Range" and page_input:
        selected_pages = []
        for p in page_input.split(","):
            p = p.strip()
            if "-" in p:
                start, end = p.split("-")
                start = int(start) - 1 if start else 0
                end = int(end) if end else -1
                if end == -1:
                    selected_pages.append(start)
                else:
                    selected_pages.extend(range(start, end))
            else:
                selected_pages.append(int(p) - 1)
    else:
        selected_pages = stable_page_map.get(page_range)
    
    # Get translated service name
    translated_service = stable_service_map.get(service, "Google")
    
    # Prepare output paths
    filename = file_path.stem
    file_mono = OUTPUT_DIR / f"{filename}-mono.pdf"
    file_dual = OUTPUT_DIR / f"{filename}-dual.pdf"
    
    # Prepare environment variables for the translator
    envs = {}
    # Copy relevant API keys and settings from ui_inputs
    for key, value in ui_inputs.items():
        if value and isinstance(value, str) and (
            "api_key" in key.lower() or 
            "apikey" in key.lower() or 
            "model" in key.lower() or 
            "url" in key.lower() or
            "host" in key.lower() or
            "endpoint" in key.lower()
        ):
            envs[key] = value
    
    # Prepare translation parameters for pdf2zh
    def progress_callback(t):
        """Callback for translation progress"""
        desc = getattr(t, "desc", "Translating...")
        if desc == "":
            desc = "Translating..."
        progress = t.n / t.total if t.total > 0 else 0
        tasks[task_id]["logs"].append(str({
            "type": "progress_update",
            "stage": desc,
            "progress": progress * 100,
            "overall_progress": progress * 100
        }))
    
    try:
        threads_num = int(threads) if threads else 4
    except (ValueError, TypeError):
        threads_num = 4
    
    # Create the translation parameters
    translate_params = {
        "files": [str(file_path)],
        "pages": selected_pages,
        "lang_in": source_lang,
        "lang_out": target_lang,
        "service": translated_service,
        "output": str(OUTPUT_DIR),
        "thread": threads_num,
        "callback": progress_callback,
        "envs": envs,
        "skip_subset_fonts": skip_subset_fonts,
        "ignore_cache": ignore_cache,
    }
    
    if vfont:
        translate_params["vfont"] = vfont
    if prompt:
        from string import Template
        translate_params["prompt"] = Template(prompt)
    
    # Try to get the model instance
    if ModelInstance is not None:
        try:
            translate_params["model"] = ModelInstance.value
        except Exception:
            pass  # Model instance not available
    
    tasks[task_id]["logs"].append(str({
        "type": "stage_summary",
        "stages": [
            {"name": "Preparing", "percent": 10},
            {"name": "Translating", "percent": 80},
            {"name": "Finalizing", "percent": 10}
        ]
    }))
    
    tasks[task_id]["logs"].append(str({
        "type": "progress_start",
        "stage": "Translating",
        "overall_progress": 0
    }))
    
    # Run translation in a thread pool to not block the event loop
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=1) as executor:
        await loop.run_in_executor(executor, lambda: pdf2zh_translate(**translate_params))
    
    tasks[task_id]["logs"].append(str({
        "type": "progress_end",
        "stage": "Translating",
        "overall_progress": 100
    }))
    
    # Check for output files
    if file_mono.exists() and not no_mono:
        tasks[task_id]["mono_pdf_path"] = str(file_mono)
    if file_dual.exists() and not no_dual:
        tasks[task_id]["dual_pdf_path"] = str(file_dual)
    
    # Fallback: look for files with language suffix pattern
    if "mono_pdf_path" not in tasks[task_id] and "dual_pdf_path" not in tasks[task_id]:
        pattern = f"{filename}*.pdf"
        matching_files = list(OUTPUT_DIR.glob(pattern))
        for pdf_file in matching_files:
            if pdf_file.name != file_path.name:
                if "-mono" in pdf_file.name:
                    tasks[task_id]["mono_pdf_path"] = str(pdf_file)
                elif "-dual" in pdf_file.name:
                    tasks[task_id]["dual_pdf_path"] = str(pdf_file)
                else:
                    # Use as mono if no specific type
                    if "mono_pdf_path" not in tasks[task_id]:
                        tasks[task_id]["mono_pdf_path"] = str(pdf_file)
    
    tasks[task_id]["status"] = "completed"
    logger.info(f"Task {task_id}: Translation completed successfully (stable backend)")


@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Return a copy without internal objects
    status_data = tasks[task_id].copy()
    if "task_object" in status_data:
        del status_data["task_object"]
    return status_data

@app.get("/api/download/{file_id}")
async def download_file(file_id: str):
    # Search for file in output dir
    # We might need a better way to map file_id to output filename
    # For now, let's assume the client knows the filename or we store it
    # But wait, run_translation stores "output_file" in task status.
    # So client can get path from status.
    
    # Let's allow downloading by path if it's in OUTPUT_DIR
    # Or better, use task_id to get the file
    pass

@app.get("/api/download_task/{task_id}")
async def download_task_result(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    # Prefer mono, fallback to dual, then to old output_file field
    file_path = None
    if "mono_pdf_path" in task and task["mono_pdf_path"]:
        file_path = Path(task["mono_pdf_path"])
    elif "dual_pdf_path" in task and task["dual_pdf_path"]:
        file_path = Path(task["dual_pdf_path"])
    elif "output_file" in task and task["output_file"]:
        file_path = Path(task["output_file"])
    
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path, filename=file_path.name)

@app.get("/api/download_task/{task_id}/mono")
async def download_task_mono(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    if "mono_pdf_path" not in task or not task["mono_pdf_path"]:
        raise HTTPException(status_code=404, detail="Mono PDF not found")
    
    file_path = Path(task["mono_pdf_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path, filename=file_path.name)

@app.get("/api/download_task/{task_id}/dual")
async def download_task_dual(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    if "dual_pdf_path" not in task or not task["dual_pdf_path"]:
        raise HTTPException(status_code=404, detail="Dual PDF not found")
    
    file_path = Path(task["dual_pdf_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path, filename=file_path.name)

# Store dev mode flag (set when server starts with --gui-dev)
_gui_dev_mode = False

# Store default backend mode: 'stable' (pdf2zh) or 'experimental' (pdf2zh_next)
# Default is 'stable' when started with pdf2zh, 'experimental' when started with pdf2zh_next --gui
_default_backend_mode = 'stable'

def set_gui_dev_mode(enabled: bool):
    global _gui_dev_mode
    _gui_dev_mode = enabled

def get_gui_dev_mode() -> bool:
    return _gui_dev_mode

def set_default_backend_mode(mode: str):
    """Set the default backend mode ('stable' or 'experimental')"""
    global _default_backend_mode
    if mode in ('stable', 'experimental'):
        _default_backend_mode = mode
    else:
        logger.warning(f"Invalid backend mode: {mode}, using 'stable'")
        _default_backend_mode = 'stable'

def get_default_backend_mode() -> str:
    return _default_backend_mode


def is_stable_backend_available() -> tuple[bool, str | None]:
    """Check if the stable pdf2zh backend is installed and available.
    
    Returns:
        Tuple of (is_available, error_message)
    """
    try:
        # Try importing the pdf2zh package
        import pdf2zh
        logger.info(f"pdf2zh package found: {pdf2zh.__file__}")
        logger.info(f"pdf2zh version: {getattr(pdf2zh, '__version__', 'unknown')}")
        
        # The translate function is in pdf2zh.gui module (not high_level)
        from pdf2zh.gui import translate as pdf2zh_translate
        logger.info("pdf2zh.gui.translate imported successfully")
        
        # Verify it's callable
        if callable(pdf2zh_translate):
            logger.info("pdf2zh stable backend is available and ready")
            return True, None
        else:
            error = "pdf2zh.gui.translate is not callable"
            logger.warning(error)
            return False, error
            
    except ImportError as e:
        error = f"ImportError: {e}"
        logger.info(f"pdf2zh stable backend not available: {error}")
        return False, error
    except Exception as e:
        error = f"Unexpected error: {e}"
        logger.warning(f"pdf2zh stable backend check failed: {error}")
        return False, error


def get_available_backends() -> dict:
    """Get information about available translation backends."""
    stable_available, stable_error = is_stable_backend_available()
    
    install_hint = None
    if not stable_available:
        install_hint = "pip install pdf2zh"
        if stable_error:
            logger.info(f"Stable backend not available: {stable_error}")
    
    return {
        "stable": {
            "available": stable_available,
            "name": "Stable (pdf2zh)",
            "description": "Original pdf2zh translation engine",
            "install_hint": install_hint,
            "error": stable_error if not stable_available else None
        },
        "experimental": {
            "available": True,  # Always available as it's the main package
            "name": "Experimental (pdf2zh_next)",
            "description": "Next-generation translation engine with BabelDOC"
        }
    }

# Get all available translation parameters for dev mode
def _get_all_translation_params():
    """Get all available translation parameters with their types and descriptions"""
    from pdf2zh_next.config.model import PDFSettings, TranslationSettings, GUISettings
    
    params = {}
    
    # Get fields from TranslationSettings
    for name, field in TranslationSettings.model_fields.items():
        params[f"translation.{name}"] = {
            "name": name,
            "category": "translation",
            "type": str(field.annotation),
            "description": field.description,
            "default": field.default
        }
    
    # Get fields from PDFSettings
    for name, field in PDFSettings.model_fields.items():
        params[f"pdf.{name}"] = {
            "name": name,
            "category": "pdf",
            "type": str(field.annotation),
            "description": field.description,
            "default": field.default
        }
    
    # Get fields from each translation engine
    for metadata in TRANSLATION_ENGINE_METADATA:
        if metadata.setting_model_type:
            engine_name = metadata.translate_engine_type
            for name, field in metadata.setting_model_type.model_fields.items():
                if name not in ("translate_engine_type", "support_llm"):
                    params[f"engine.{engine_name}.{name}"] = {
                        "name": name,
                        "category": f"engine_{engine_name}",
                        "type": str(field.annotation),
                        "description": field.description if hasattr(field, 'description') else None,
                        "default": field.default if hasattr(field, 'default') else None
                    }
    
    return params

@app.get("/api/config")
async def get_config():
    try:
        # Get pdf2zh_next version
        from pdf2zh_next import __version__ as pdf2zh_next_version
        
        # Get backend availability info
        backends = get_available_backends()
        stable_available = backends["stable"]["available"]
        
        # Try to get pdf2zh (stable) version
        pdf2zh_version = None
        if stable_available:
            try:
                from pdf2zh import __version__ as stable_version
                pdf2zh_version = stable_version
            except ImportError:
                pdf2zh_version = "not installed"
        else:
            pdf2zh_version = "not installed"
        
        # If stable is not available and default is stable, switch to experimental
        effective_default = _default_backend_mode
        if effective_default == "stable" and not stable_available:
            effective_default = "experimental"
        
        config_data = {
            "languages": lang_map,
            "services": [x.translate_engine_type for x in TRANSLATION_ENGINE_METADATA],
            "dev_mode": _gui_dev_mode,
            "default_backend": effective_default,
            "backends": backends,
            "versions": {
                "stable": pdf2zh_version,
                "experimental": pdf2zh_next_version,
            },
        }
        
        # Add detailed params info in dev mode
        if _gui_dev_mode:
            config_data["all_params"] = _get_all_translation_params()
        
        return config_data
    except Exception as e:
        logger.error(f"Error getting config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def get_health():
    """Get server health information including CPU load and memory usage"""
    try:
        # Get CPU usage (percent over 0.1 seconds for faster response)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024 ** 3)
        memory_total_gb = memory.total / (1024 ** 3)
        
        # Count active tasks
        active_tasks = sum(1 for task in tasks.values() if task.get("status") == "processing")
        total_tasks = len(tasks)
        pending_tasks = sum(1 for task in tasks.values() if task.get("status") == "pending")
        
        # Determine server status
        if active_tasks > 0:
            status = "busy"
        elif any(task.get("status") == "failed" for task in tasks.values()):
            status = "error"
        else:
            status = "ready"
        
        return {
            "status": status,
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory_percent, 1),
            "memory_used_gb": round(memory_used_gb, 2),
            "memory_total_gb": round(memory_total_gb, 2),
            "active_tasks": active_tasks,
            "pending_tasks": pending_tasks,
            "total_tasks": total_tasks,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting health info: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }


@app.get("/api/debug/backends")
async def debug_backends():
    """Debug endpoint to check backend availability with detailed information."""
    import sys
    import importlib
    
    result = {
        "backends": get_available_backends(),
        "python_path": sys.path[:5],  # First 5 entries
        "installed_packages": {}
    }
    
    # Check if pdf2zh is in sys.modules
    result["pdf2zh_in_sys_modules"] = "pdf2zh" in sys.modules
    
    # Try to find pdf2zh package info
    try:
        import importlib.metadata
        try:
            pdf2zh_dist = importlib.metadata.distribution("pdf2zh")
            result["installed_packages"]["pdf2zh"] = {
                "version": pdf2zh_dist.version,
                "location": str(pdf2zh_dist._path) if hasattr(pdf2zh_dist, '_path') else "unknown"
            }
        except importlib.metadata.PackageNotFoundError:
            result["installed_packages"]["pdf2zh"] = {"error": "Package not found in metadata"}
    except Exception as e:
        result["installed_packages"]["pdf2zh"] = {"error": str(e)}
    
    # Try direct import with detailed error
    try:
        # Clear any cached import
        if "pdf2zh" in sys.modules:
            result["pdf2zh_cached"] = True
        
        import pdf2zh
        result["pdf2zh_import"] = {
            "success": True,
            "file": getattr(pdf2zh, "__file__", "unknown"),
            "version": getattr(pdf2zh, "__version__", "unknown")
        }
        
        # Try to import gui module (where translate function is)
        try:
            from pdf2zh import gui
            result["pdf2zh_gui"] = {
                "success": True,
                "file": getattr(gui, "__file__", "unknown"),
                "has_translate": hasattr(gui, "translate")
            }
            
            if hasattr(gui, "translate"):
                result["pdf2zh_translate"] = {
                    "callable": callable(gui.translate),
                    "type": str(type(gui.translate))
                }
        except Exception as e:
            result["pdf2zh_gui"] = {"error": str(e)}
            
    except ImportError as e:
        result["pdf2zh_import"] = {"error": f"ImportError: {e}"}
    except Exception as e:
        result["pdf2zh_import"] = {"error": f"Exception: {e}"}
    
    return result


async def run_server(host="0.0.0.0", port=8000, gui_dev: bool = False, default_backend: str = 'experimental'):
    import uvicorn
    import webbrowser
    import threading
    
    # Set dev mode flag
    set_gui_dev_mode(gui_dev)
    if gui_dev:
        logger.info("GUI Development Mode enabled")
    
    # Set default backend mode
    set_default_backend_mode(default_backend)
    logger.info(f"Default backend mode: {default_backend}")
    
    # Check and log backend availability at startup
    backends = get_available_backends()
    logger.info(f"Backend availability check:")
    logger.info(f"  - Stable (pdf2zh): {'Available' if backends['stable']['available'] else 'Not available'}")
    if not backends['stable']['available'] and backends['stable'].get('error'):
        logger.info(f"    Error: {backends['stable']['error']}")
    logger.info(f"  - Experimental (pdf2zh_next): Available")
    
    # Determine frontend path
    # Assuming structure:
    # repo_root/
    #   pdf2zh_next/
    #     server.py
    #   frontend/
    #     dist/
    
    frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
    
    # Fallback to current directory if relative path works (e.g. running from root)
    if not frontend_dist.exists():
        if Path("frontend/dist").exists():
            frontend_dist = Path("frontend/dist")

    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
        logger.info(f"Serving frontend from {frontend_dist}")
    else:
        logger.warning(f"Frontend dist not found at {frontend_dist}. Run 'bun run build' in frontend directory.")
    
    # Function to open browser after a short delay
    def open_browser():
        import time
        time.sleep(1.5)  # Wait for server to start
        url = f"http://127.0.0.1:{port}/"
        logger.info(f"Opening browser at {url}")
        webbrowser.open(url)
    
    # Start browser opening in a separate thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
        
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_server())
