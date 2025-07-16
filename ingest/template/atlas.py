from ingest.template.base import DataCiteTemplate, DatasetFileMetadata


class TheAtlasOfEconomicComplexityTemplate(DataCiteTemplate):
    template = [
        DatasetFileMetadata(
            source="https://doi.org/10.7910/DVN/XTAQMC",
            target="rankings/",
            attribution="""
                The Growth Lab at Harvard University, 2025, "Growth Projections and Complexity Rankings", https://doi.org/10.7910/DVN/XTAQMC, Harvard Dataverse
            """,
        ),
        DatasetFileMetadata(
            source="https://doi.org/10.7910/DVN/T4CHWJ",
            target="HS92/",
            attribution="""
                The Growth Lab at Harvard University, 2025, "International Trade Data (HS92)", https://doi.org/10.7910/DVN/T4CHWJ, Harvard Dataverse
            """,
        ),
        DatasetFileMetadata(
            source="https://doi.org/10.7910/DVN/YAVJDF",
            target="HS12/",
            attribution="""
                The Growth Lab at Harvard University, 2025, "International Trade Data (HS12)", https://doi.org/10.7910/DVN/YAVJDF, Harvard Dataverse
            """,
        ),
        DatasetFileMetadata(
            source="https://doi.org/10.7910/DVN/H8SFD2",
            target="SITC/",
            attribution="""
                The Growth Lab at Harvard University, 2025, "International Trade Data (SITC, Rev. 2)", https://doi.org/10.7910/DVN/H8SFD2, Harvard Dataverse
            """,
        ),
        DatasetFileMetadata(
            source="https://doi.org/10.7910/DVN/NDDMSN",
            target="services_unilateral/",
            attribution="""
                The Growth Lab at Harvard University, 2025, "International Trade Data (Services)", https://doi.org/10.7910/DVN/NDDMSN, Harvard Dataverse
            """,
        ),
        DatasetFileMetadata(
            source="https://doi.org/10.7910/DVN/3BAL1O",
            target="classifications/",
            attribution="""
                The Growth Lab at Harvard University, 2025, "Classifications Data", https://doi.org/10.7910/DVN/3BAL1O, Harvard Dataverse
            """,
        ),
        DatasetFileMetadata(
            source="https://doi.org/10.7910/DVN/FCDZBN",
            target="product_space/",
            attribution="""
                The Growth Lab at Harvard University, 2025, "Product Space Networks", https://doi.org/10.7910/DVN/FCDZBN, Harvard Dataverse
            """,
        ),
    ]
