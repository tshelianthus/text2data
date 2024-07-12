from openai import OpenAI
import requests
import logging


class AigcQueryParser:
    def __init__(self, config, user_aigc="DEEP_SEEK", schema_infos="NOTHING"):
        self.config = config

        self.db_alias = self.config["DB_SRC"]["PRJ_DATA"]["DB_ALIAS"]
        self.db_config = self.config["DB_URI"].get(self.db_alias)
        self.db_dialect = self.db_config["DIALECT"]

        self.api_url = self.config["AIGC_API"][user_aigc]["API_BASE_URL"]
        self.api_key = self.config["AIGC_API"][user_aigc]["API_KEY"]
        self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)
        self.schema_infos = schema_infos

    def extract_sql_code(self, response):
        start_marker = '```sql\n'
        end_marker = '\n```'

        start_index = response.find(start_marker) + len(start_marker)
        end_index = response.find(end_marker, start_index)

        if start_index == -1 or end_index == -1:
            return None  # 如果没有找到SQL代码，返回None

        sql_code = response[start_index:end_index]
        return sql_code


    def parse_query_to_sql(self, user_query, user_model="deepseek-coder"):
        

        # 读取自定义语料文件
        custom_corpus_path = "data/custom_corpus.txt"
        with open(custom_corpus_path, 'r', encoding='utf-8') as file:
            custom_corpus = file.read().strip()
        
        system_role_set = f"You are a helpful '{self.db_dialect}' sql assistant."
        system_schema_set = f"{self.schema_infos}"

        request_messages = [
            {"role": "system", "content": system_role_set},
            {"role": "system", "content": "This is App Database Schema"},
            {"role": "system", "content": system_schema_set},
            {"role": "system", "content": custom_corpus},
            {"role": "user", "content": "My request is, Please return SQL for it."},
            {"role": "user", "content": user_query},
        ]
        response = self.client.chat.completions.create(
            model=user_model,
            messages=request_messages,
            stream=False,
            temperature=1
        )

        response_content = response.choices[0].message.content
        extract_sql = self.extract_sql_code(response_content)

        return extract_sql
