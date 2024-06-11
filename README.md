# PoTo: A Hybrid Andersen's Points-to Analysis for Python

If accepted we'll submit an artifact for evaluation

## Directory

* data
    * DL_aggregated
        - Aggregated type results from DL's artifact
    * Figures
        - Figures from the paper
    * PoTo_graph_pkl
        - Point-to graph from the PoTo analysis (missing some pkl that are very large in size)
    * PoToPlus_compare
        - RQ2: Equivalence comparison between PoTo+ and 4 techniques
    * processed_PoTo_type
        - Type results from PoTo analysis
    * PT_test
        - Generated tests dir from 5 packages test suites to match our need that each test function is an entry point

* orig_pro_dynamic
    * Source codes of the 10 packages, taken from [DLInfer's package](https://zenodo.org/records/7575545).
    * anaconda, ansible, bokeh, cerberus, invoke, mtgjson, pygal, sc2, wemake_python_styleguide, zfsp
    * include custom test cases for the 5 packages (cerberus, mtgjson, pygal, sc2, zfsp)