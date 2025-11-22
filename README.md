<div align="center">

<img src="./docs/images/gui-vue.jpeg" alt="banner"/>

<h2 id="title">Experimental GUI for PDFMathTranslate-next</h2>

In this fork, active developers are working on a Vue.js GUI for PDFMathTranslate-next, which brings a more firendly user experience, substantially improved quality, and much more features.

This fork, however, is still under development and is not stable. It is not recommended to use it for production.

<p>
  <!-- PyPI -->
  <a href="https://pypi.org/project/pdf2zh-next/">
    <img src="https://img.shields.io/pypi/v/pdf2zh-next"></a>
  <a href="https://pepy.tech/projects/pdf2zh-next">
    <img src="https://static.pepy.tech/badge/pdf2zh-next"></a>
  <a href="https://hub.docker.com/repository/docker/awwaawwa/pdfmathtranslate-next/tags">
    <img src="https://img.shields.io/docker/pulls/awwaawwa/pdfmathtranslate-next"></a>
  <a href="https://hellogithub.com/repository/8ec2cfd3ef744762bf531232fa32bc47" target="_blank"><img src="https://api.hellogithub.com/v1/widgets/recommend.svg?rid=8ec2cfd3ef744762bf531232fa32bc47&claim_uid=JQ0yfeBNjaTuqDU&theme=small" alt="Featured｜HelloGitHub" /></a>
  <!-- <a href="https://gitcode.com/PDFMathTranslate/PDFMathTranslate-next/overview">
    <img src="https://gitcode.com/PDFMathTranslate/PDFMathTranslate-next/star/badge.svg"></a> -->
  <!-- <a href="https://huggingface.co/spaces/reycn/PDFMathTranslate-Docker">
    <img src="https://img.shields.io/badge/%F0%9F%A4%97-Online%20Demo-FF9E0D"></a> -->
  <!-- <a href="https://www.modelscope.cn/studios/AI-ModelScope/PDFMathTranslate"> -->
    <!-- <img src="https://img.shields.io/badge/ModelScope-Demo-blue"></a> -->
  <!-- <a href="https://github.com/PDFMathTranslate/PDFMathTranslate-next/pulls">
    <img src="https://img.shields.io/badge/contributions-welcome-green"></a> -->
  <a href="https://t.me/+Z9_SgnxmsmA5NzBl">
    <img src="https://img.shields.io/badge/Telegram-2CA5E0?style=flat-squeare&logo=telegram&logoColor=white"></a>
  <!-- License -->
  <a href="./LICENSE">
    <img src="https://img.shields.io/github/license/PDFMathTranslate/PDFMathTranslate-next"></a>
  <a href="https://hosted.weblate.org/engage/pdfmathtranslate-next/">
    <img src="https://hosted.weblate.org/widget/pdfmathtranslate-next/svg-badge.svg" alt="translation status" /></a>
    <a href="https://deepwiki.com/PDFMathTranslate/PDFMathTranslate-next"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

<a href="https://trendshift.io/repositories/12424" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12424" alt="Byaidu%2FPDFMathTranslate | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

</div>

PDF scientific paper translation and bilingual comparison.

- 📊 Preserve formulas, charts, table of contents, and annotations _([preview](#preview))_.
- 🌐 Support [multiple languages](https://pdf2zh-next.com/supported_languages.html), and diverse [translation services](https://pdf2zh-next.com/advanced/Documentation-of-Translation-Services.html).
- 🤖 Provides [commandline tool](https://pdf2zh-next.com/getting-started/USAGE_commandline.html), [interactive user interface](https://pdf2zh-next.com/getting-started/USAGE_webui.html), and [Docker](https://pdf2zh-next.com/getting-started/INSTALLATION_docker.html)

<!-- Feel free to provide feedback in [GitHub Issues](https://github.com/PDFMathTranslate/PDFMathTranslate-next/issues) or [Telegram Group](https://t.me/+Z9_SgnxmsmA5NzBl). -->

> [!WARNING]
>
> This project is provided "as is" under the [AGPL v3](https://github.com/PDFMathTranslate/PDFMathTranslate-next/blob/main/LICENSE) license, and no guarantees are provided for the quality and performance of the program. **The entire risk of the program's quality and performance is borne by you.** If the program is found to be defective, you will be responsible for all necessary service, repair, or correction costs.
>
> Due to the maintainers' limited energy, we do not provide any form of usage assistance or problem-solving. Related issues will be closed directly! (Pull requests to improve project documentation are welcome; bugs or friendly issues that follow the issue template are not affected by this)


For details on how to contribute, please consult the [Contribution Guide](https://pdf2zh-next.com/community/Contribution-Guide.html).

<h2 id="updates">Updates</h2>

- [Jun. 4, 2025] The project is renamed and move to [PDFMathTranslate/PDFMathTranslate-next](https://github.com/PDFMathTranslate/PDFMathTranslate-next) (by [@awwaawwa](https://github.com/awwaawwa))
- [Mar. 3, 2025] Experimental support for the new backend [BabelDOC](https://github.com/funstory-ai/BabelDOC) WebUI added as an experimental option (by [@awwaawwa](https://github.com/awwaawwa))
- [Feb. 22 2025] Better release CI and well-packaged windows-amd64 exe (by [@awwaawwa](https://github.com/awwaawwa))
- [Dec. 24 2024] The translator now supports local models on [Xinference](https://github.com/xorbitsai/inference) _(by [@imClumsyPanda](https://github.com/imClumsyPanda))_
- [Dec. 19 2024] Non-PDF/A documents are now supported using `-cp` _(by [@reycn](https://github.com/reycn))_
- [Dec. 13 2024] Additional support for backend by _(by [@YadominJinta](https://github.com/YadominJinta))_
- [Dec. 10 2024] The translator now supports OpenAI models on Azure _(by [@yidasanqian](https://github.com/yidasanqian))_

<h2 id="preview">Preview</h2>

<div align="center">
<!-- <img src="./docs/images/preview.gif" width="80%"  alt="preview"/> -->
<img src="https://s.immersivetranslate.com/assets/r2-uploads/images/babeldoc-preview.png" width="80%"/>
</div>

<h2 id="demo">Online Service 🌟</h2>

> [!NOTE]
>
> pdf2zh 2.0 does not currently provide an online demo

You can try our application out using either of the following demos:

- [v1.x Public free service](https://pdf2zh.com/) online without installation _(recommended)_.
- [Immersive Translate - BabelDOC](https://app.immersivetranslate.com/babel-doc/) Free usage quota is available; please refer to the FAQ section on the page for details. _(recommended)_
<!-- - [Demo hosted on HuggingFace](https://huggingface.co/spaces/reycn/PDFMathTranslate-Docker)
- [Demo hosted on ModelScope](https://www.modelscope.cn/studios/AI-ModelScope/PDFMathTranslate) without installation. -->

Note that the computing resources of the demo are limited, so please avoid abusing them.

<h2 id="install">Installation and Usage</h2>

### Installation

1. [**Windows EXE**](https://pdf2zh-next.com/getting-started/INSTALLATION_winexe.html) <small>Recommand for Windows</small>
2. [**Docker**](https://pdf2zh-next.com/getting-started/INSTALLATION_docker.html) <small>Recommand for Linux</small>
3. [**uv** (a Python package manager)](https://pdf2zh-next.com/getting-started/INSTALLATION_uv.html) <small>Recommand for macOS</small>

---

### Usage

1. [Using **WebUI**](https://pdf2zh-next.com/getting-started/USAGE_webui.html)
2. [Using **Zotero Plugin**](https://github.com/guaguastandup/zotero-pdf2zh) (Third party program)
3. [Using **Commandline**](https://pdf2zh-next.com/getting-started/USAGE_commandline.html)

For different use cases, we provide distinct methods to use our program. Check out [this page](./getting-started/getting-started.md) for more information.

<h2 id="usage">Advanced Options</h2>

For detailed explanations, please refer to our document about [Advanced Usage](https://pdf2zh-next.com/advanced/advanced.html) for a full list of each option.

<h2 id="downstream">Secondary Development (APIs)</h2>

> [!NOTE]
>
> Currently, no relevant documentation is provided. It will be supplemented later. Please wait patiently.


<!-- For downstream applications, please refer to our document about [API Details](./docs/APIS.md) for futher information about:

- [Python API](./docs/APIS.md#api-python), how to use the program in other Python programs
- [HTTP API](./docs/APIS.md#api-http), how to communicate with a server with the program installed -->

<h2 id="langcode">Language Code</h2>

If you don't know what code to use to translate to the language you need, check out [this documentation](https://pdf2zh-next.com/advanced/Language-Codes.html)

<!-- 
<h2 id="todo">TODOs</h2>

- [ ] Parse layout with DocLayNet based models, [PaddleX](https://github.com/PaddlePaddle/PaddleX/blob/17cc27ac3842e7880ca4aad92358d3ef8555429a/paddlex/repo_apis/PaddleDetection_api/object_det/official_categories.py#L81), [PaperMage](https://github.com/allenai/papermage/blob/9cd4bb48cbedab45d0f7a455711438f1632abebe/README.md?plain=1#L102), [SAM2](https://github.com/facebookresearch/sam2)

- [ ] Fix page rotation, table of contents, format of lists

- [ ] Fix pixel formula in old papers

- [ ] Async retry except KeyboardInterrupt

- [ ] Knuth–Plass algorithm for western languages

- [ ] Support non-PDF/A files

- [ ] Plugins of [Zotero](https://github.com/zotero/zotero) and [Obsidian](https://github.com/obsidianmd/obsidian-releases) -->

<h2 id="acknowledgement">Acknowledgements</h2>

- [Immersive Translation](https://immersivetranslate.com) sponsors monthly Pro membership redemption codes for active contributors to this project, see details at: [CONTRIBUTOR_REWARD.md](https://github.com/funstory-ai/BabelDOC/blob/main/docs/CONTRIBUTOR_REWARD.md)

- [SiliconFlow](https://siliconflow.cn) provides a free translation service for this project, powered by large language models (LLMs).

- 1.x version: [Byaidu/PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate)


- backend: [BabelDOC](https://github.com/funstory-ai/BabelDOC)

- PDF Library: [PyMuPDF](https://github.com/pymupdf/PyMuPDF)

- PDF Parsing: [Pdfminer.six](https://github.com/pdfminer/pdfminer.six)

- PDF Preview: [Gradio PDF](https://github.com/freddyaboulton/gradio-pdf)

- Layout Parsing: [DocLayout-YOLO](https://github.com/opendatalab/DocLayout-YOLO)

- PDF Standards: [PDF Explained](https://zxyle.github.io/PDF-Explained/), [PDF Cheat Sheets](https://pdfa.org/resource/pdf-cheat-sheets/)

- Multilingual Font: see [BabelDOC-Assets](https://github.com/funstory-ai/BabelDOC-Assets)

- [Asynchronize](https://github.com/multimeric/Asynchronize/tree/master?tab=readme-ov-file)

- [Rich logging with multiprocessing](https://github.com/SebastianGrans/Rich-multiprocess-logging/tree/main)

- Documentation i18n using [Weblate](https://hosted.weblate.org/projects/pdfmathtranslate-next/) 


<h2 id="conduct">Before submit your code</h2>

We welcome the active participation of contributors to make pdf2zh better. Before you are ready to submit your code, please refer to our [Code of Conduct](https://pdf2zh-next.com/community/CODE_OF_CONDUCT.html) and [Contribution Guide](https://pdf2zh-next.com/community/Contribution-Guide.html).

<h2 id="contrib">Contributors</h2>

<a href="https://github.com/PDFMathTranslate/PDFMathTranslate-next/graphs/contributors">
  <img src="https://opencollective.com/PDFMathTranslate/contributors.svg?width=890&button=false" />
</a>

![Alt](https://repobeats.axiom.co/api/embed/45529651750579e099960950f757449a410477ad.svg "Repobeats analytics image")

<h2 id="star_hist">Star History</h2>

<a href="https://star-history.com/#PDFMathTranslate/PDFMathTranslate-next&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=PDFMathTranslate/PDFMathTranslate-next&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=PDFMathTranslate/PDFMathTranslate-next&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=PDFMathTranslate/PDFMathTranslate-next&type=Date"/>
 </picture>
</a>
