import logging
from sqlalchemy import (
    MetaData,
    create_engine,
    Column,
    Integer,
    text,
    String,
    inspect,
    text,
)
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from jinja2 import Environment, FileSystemLoader
import yaml
import json
import re


class Database:
    def __init__(self, config):
        self.config = config
        self.db_alias = self.config["DB_SRC"]["PRJ_DATA"]["DB_ALIAS"]
        self.db_name = self.config["DB_SRC"]["PRJ_DATA"]["DB_NAME"]
        self.db_schema = self.config["DB_SRC"]["PRJ_DATA"]["DB_SCHEMA"]
        self.db_uri = self.get_db_uri(db_alias=self.db_alias, db_name=self.db_name)

        try:
            self.engine = create_engine(self.db_uri, pool_size=10, max_overflow=20)
            self.Session = sessionmaker(bind=self.engine)
            self.inspector = inspect(self.engine)

            self.engine, self.session = self.db_connect(
                DB_URI=self.db_uri, pool_size=10, max_overflow=20
            )
            self.inspector = inspect(self.engine)

            logging.info("Database connect successfully.")
        except Exception as e:
            logging.error(f"Failed to connect Database. Error: {e}")
            raise

    def db_connect(self, DB_URI, pool_size=8, max_overflow=0):
        """创建数据库连接，如果失败，返回空，并打印错误信息

        Args:
            DB_URI(str):资源请求字符串，形如 postgresql://username:password@hostaddress:port/dbname
            pool_size(int):连接池大小, 默认为 8
            max_overflow (int): 连接池中允许的最大溢出连接数，默认为 10
        Examples:
            db_connect(uri)
        Returns:
            engine, session
        Raises:
            连接失败
        """
        try:
            engine = create_engine(
                DB_URI, max_overflow=max_overflow, pool_size=pool_size, pool_recycle=-1
            )

            SessionFactory = sessionmaker(bind=engine)
            session = scoped_session(SessionFactory)

            return engine, session

        except Exception as e:
            logging.error(f"Failed to connect Database. Error: {e}")
            raise

    def get_db_uri(self, db_alias, db_name=""):
        # Read the configuration file
        CONFIG_FILE = "configs/config.yaml"
        with open(CONFIG_FILE, "r") as config_file:
            config = yaml.safe_load(config_file)

        # Get the database connection parameters
        db_config = config["DB_URI"].get(db_alias)

        if not db_config:
            raise ValueError(
                f"Database configuration '{db_alias}' not found in the config file, Please check the config file check the db_alias."
            )

        if db_config["DIALECT"] == "doris":
            db_config["DIALECT"] = "mysql+pymysql"
        if db_config["DIALECT"] == "postgres":
            db_config["DIALECT"] = "postgresql"

        # Build the connection string
        db_params = {
            "dialect": db_config["DIALECT"],
            "user": db_config["USER"],
            "password": db_config["PASSWORD"],
            "host": db_config["HOST"],
            "port": db_config["PORT"],
            "db_name": db_name,
        }

        db_uri = "{dialect}://{user}:{password}@{host}:{port}/{db_name}".format(
            **db_params
        )
        return db_uri


    def execute_query(self, query, params=None):
        # 执行SQL安全检查
        is_safe_sql = self.safe_sql_ver(query)

        if is_safe_sql:

            logging.info("SQL security check passed.")

            session = self.Session()
            try:
                if params:
                    result = session.execute(text(query), params)
                else:
                    result = session.execute(text(query))
                session.commit()

                # 获取列名和数据
                columns = result.keys()
                data = result.fetchall()

                logging.info("Query executed successfully.")

                return data, columns
            except Exception as e:
                session.rollback()
                logging.error(f"Error executing query: {e}")
                raise
            finally:
                session.close()
                logging.info("Session closed.")
        else:
            logging.info("SQL security check not passed.")
            raise Exception(f"SQL安全验证未通过.")


    def generate_db_schema_json(
        self, db_name, schema="public", output_file="data/db_schema.json"
    ):

        schema_exists = self.db_schema in self.inspector.get_schema_names()
        if not schema_exists:
            logging.info(f"ERROR - Schema {self.db_schema} does not exist.")
            raise Exception(f"ERROR - Schema {self.db_schema} does not exist.")

        schema_info = {db_name: {"tables": {}}}
        tables = self.inspector.get_table_names(schema=schema)

        for table_name in tables:
            columns = self.inspector.get_columns(table_name, schema=self.db_schema)
            column_info = {}
            for column in columns:
                column_info[column["name"]] = {
                    "type": str(column["type"]),
                    "description": column.get("comment", "No description"),
                }
            schema_info[self.db_name]["tables"][table_name] = {
                "columns": column_info,
                "description": "No description",
            }

        with open(output_file, "w") as outfile:
            json.dump(schema_info, outfile, indent=4)
        logging.info(f"Database schema JSON generated and saved to {output_file}")
        return schema_info

    def safe_sql_ver(self, sql):

        is_safe = True
        # 定义不允许的SQL关键字和模式
        disallowed_keywords = [
            r"\bINSERT\b",
            r"\bUPDATE\b",
            r"\bDELETE\b",
            r"\bDROP\b",
            r"\bALTER\b",
            r"\bCREATE\b",
            r"\bTRUNCATE\b",
            r"\bEXEC\b",
            r"\bUNION\b",
            r"\bSELECT\s+\*\s+FROM\b",
        ]

        # 检查是否包含不允许的关键字
        for pattern in disallowed_keywords:
            if re.search(pattern, sql, re.IGNORECASE):
                is_safe = False

        return is_safe
