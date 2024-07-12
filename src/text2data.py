import streamlit as st
import logging

import pandas as pd
import json

from src.config import Config
from src.database import Database
from src.aigc_query import AigcQueryParser


class Text2DataApp:
    def __init__(
        self, config_path="configs/config.yaml", schema_path="data/db_schema.json"
    ):

        # parse config
        self.config = Config(config_path)
        self.db_name = self.config["DB_SRC"]["PRJ_DATA"]["DB_NAME"]
        self.schema = self.config["DB_SRC"]["PRJ_DATA"]["DB_SCHEMA"]

        self.db_conn = Database(config=self.config)
        
        self.schema_infos = self.db_conn.generate_db_schema_json(
            db_name=self.db_name,
            schema=self.schema
        )
        
        self.query_parser = AigcQueryParser(
            config=self.config, schema_infos=self.schema_infos
        )
        
        self.schema_path = schema_path

    def load_db_schema(self):
        with open(self.schema_path, "r") as schema_file:
            schema = json.load(schema_file)
        return schema

    def run(self):
        st.title("Text2Data")

        user_query = st.text_area("Enter your query")
        if st.button("Submit"):
            try:
                sql_query = self.query_parser.parse_query_to_sql(user_query, user_model="deepseek-chat")
                
                logging.info(f"Success grant sql.")
                data, columns = self.db_conn.execute_query(sql_query)
                logging.info(f"Success get data.")

                # 返回SQL语句结果
                st.write("SQL:")  # 添加提示语
                st.code(sql_query, language='sql', line_numbers=True)

                if data:
                    df = pd.DataFrame(data, columns=columns)
                    st.dataframe(df)

                    # 提供复制功能
                    copy_text = df.to_csv(sep="\t", index=False)
                    st.text_area("Copy the table below to Excel:", copy_text, height=200)

                else:
                    raise Exception(f"No data returned.\n请调整输入词，尽可能精确地描述需求.")

                
            except Exception as e:
                logging.info("程序执行")
                st.error(f"ERROR: {e}")
