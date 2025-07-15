from ingest.template.base import DataCiteTemplate, DatasetFileMetadata


class TheAtlasOfEconomicComplexityTemplate(DataCiteTemplate):
    template = [
        DatasetFileMetadata(
            source="https://doi.org/10.7910/DVN/XTAQMC",
            target="rankings/",
            attribution="""
                The Growth Lab at Harvard University, 2025, "Growth Projections and Complexity Rankings", https://doi.org/10.7910/DVN/XTAQMC, Harvard Dataverse
            """,
        )
    ]
