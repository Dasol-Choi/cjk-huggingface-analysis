# cjk-huggingface-analysis
[![arXiv](https://img.shields.io/badge/arXiv-2311.02240-b31b1b.svg)](https://arxiv.org/abs/2507.04329)

This repository contains the data collection and analysis code for the paper:

📄 [**No Language Data Left Behind: A Comparative Study of CJK Language Datasets in the Hugging Face Ecosystem**](https://arxiv.org/abs/2507.04329)  

---

## 📦 Dataset Access

We publicly release the structured metadata and dataset card contents for 3,300+ datasets from the Hugging Face Hub, covering:

- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- English (en, reference)

Access the full dataset here:

👉 **[https://huggingface.co/datasets/Dasool/huggingface-cjk-metadata](https://huggingface.co/datasets/Dasool/huggingface-cjk-metadata)**

The dataset includes:
- `dataset_meta_*.csv`: structured metadata (size, license, tasks, authorship, etc.)
- `dataset_cards_*.csv`: raw README and YAML contents from Hugging Face

---

## 🧭 Project Overview

This project provides a large-scale, cross-linguistic analysis of the Hugging Face dataset ecosystem for Chinese, Japanese, and Korean.  
We examine:

- Dataset scale and composition  
- Licensing patterns and documentation quality  
- Instruction tuning trends over time  
- Cultural and institutional development patterns

All data was collected via the Hugging Face Datasets API and analyzed using structured scripts and notebooks.

---

## 📁 Repository Structure
```
cjk-huggingface-analysis/
├── scripts/
│ ├── hugging_card_scraping.py 
│ └── hugging_metadata_scraping.py 
│
├── analysis/
│ ├── analysis_datasetcard.ipynb 
│ └── analysis_metadata.ipynb 
│ 
└── README.md 
```

## 📝 Citation
```bibtex
@misc{choi2025languagedataleftbehind,
      title={No Language Data Left Behind: A Comparative Study of CJK Language Datasets in the Hugging Face Ecosystem}, 
      author={Dasol Choi and Woomyoung Park and Youngsook Song},
      year={2025},
      eprint={2507.04329},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2507.04329}, 
}
```

## 📬 Contact
- dasolchoi@yonsei.ac.kr
