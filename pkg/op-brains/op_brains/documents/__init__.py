from op_brains.documents.optimism import (
    FragmentsProcessingStrategy,
    SummaryProcessingStrategy
)

# this list contains lists that are ordered by priority level
# each inner list contains some sources that have the same priority level (entries will be ordered by last_date)
chat_sources = [ 
    [FragmentsProcessingStrategy,],
    [SummaryProcessingStrategy,]
]

import pandas as pd

class DataExporter:
    @staticmethod
    def get_dataframe():
        context_df = []
        for priority_class in chat_sources:
            dfs_class = []
            for source in priority_class:
                df_source = source.dataframe_process()

                if not df_source.columns.tolist() == ["url", "last_date", "content", "type_db_info"]:
                    raise ValueError(f"DataFrame columns are not as expected: {df_source.columns.tolist()}")
                
                dfs_class.append(df_source)
            
            dfs_class = pd.concat(dfs_class)
            dfs_class = dfs_class.sort_values(by="last_date", ascending=False)
            context_df.append(dfs_class)
        
        context_df = pd.concat(context_df)
        return context_df


    @staticmethod
    def get_langchain_documents():
        out = {}
        for source in [x for xs in chat_sources for x in xs]:
            documents = source.langchain_process()
            if isinstance(documents, dict):
                documents = {f"{source.name_source}_{key}": value for key, value in documents.items()}
            elif isinstance(documents, list):
                documents = {source.name_source: documents}
            else:
                raise ValueError(f"Unexpected type of documents: {type(documents)}")
            
            out.update(documents)
            
        return out