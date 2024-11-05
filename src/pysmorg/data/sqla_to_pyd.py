import re
from collections import defaultdict
from pydantic import BaseModel, create_model
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from sqlalchemy.ext.declarative import DeclarativeMeta
from typing import Optional
from functools import partial

"""
Wrote this a long time ago to convert SQLAlchemy models to Pydantic models. It worked well but it boggles my addled mind :D
How it seems to reference a `table_models` which is surely "in construction" to refer to child pydantic models is beyond me...
"""
# TODO: Fix this mess

class InvalidJoinError(Exception): ...

Patterns = list[str | re.Pattern[str]]

def is_relationship(column):
    return isinstance(inspect(column).property, RelationshipProperty)

class TableModel(BaseModel):
    class Config:
        from_attributes: bool = True

    @classmethod
    def create_from_table(cls, Table: type[DeclarativeMeta]):
        return partial(
            cls.__create_model_from_table, 
            Table=Table,
            BaseModel=cls
        )

    @staticmethod
    def __create_model_from_table(
        Table: type[DeclarativeMeta],
        BaseModel: type[BaseModel],
        include: Patterns | None = None,
        exclude: Patterns | None = None,
        join: list[str] | None = None,
        skip_foreign_keys: bool = False,
    ) -> type[BaseModel]:

        include = include or []
        exclude = exclude or []
        join = join or []
        
        def is_field_matched(field_name: str, patterns: Patterns):
            for pattern in patterns:
                if isinstance(pattern, str):
                    if field_name == pattern:
                        return True
                elif isinstance(pattern, re.Pattern):
                    if pattern.match(field_name):
                        return True
            return False

        # Extract SQLAlchemy mapped attributes
        fields = {}
        for key, attr in Table.__mapper__.all_orm_descriptors.items():

            # Exclude fields
            if is_field_matched(key, exclude):
                continue

            # Include fields
            if include and not is_field_matched(key, include):
                continue
            
            # Only include columns, not relationships
            if not isinstance(attr.property, ColumnProperty):
                continue

            column = attr.property.columns[0]

            # Skip foreign keys if skip_foreign_keys is True
            if skip_foreign_keys and column.foreign_keys:
                continue

            if column.nullable:
                type_ = Optional[column.type.python_type]
            else:
                type_ = column.type.python_type

            fields[key] = (type_, None if column.nullable else ...)

        if join:
            joins = defaultdict(list)
            # seperate joins into current table ["."] and nested tables
            for j in join:
                split = j.split(".", 1)
                if len(split) == 1:
                    joins["."].append(split[0]) # current table
                else:
                    joins[split[0]].append(split[1]) # nested table
            for key in joins["."]:
                if not is_relationship(getattr(Table, key)):
                    raise InvalidJoinError(f"Attribute {key} is not a relationship on {Table}.")
                
                relationship = getattr(Table, key)

                if relationship.property.uselist:
                    fields[key] = (list[table_models[relationship.property.mapper.class_](join=joins.get(key, None))], [])
                else:
                    fields[key] = (Optional[table_models[relationship.property.mapper.class_](join=joins.get(key, None))], None)

        Model = create_model(
            f"{Table.__name__}Model",
            **fields,
            __base__=BaseModel,
        )
        return Model

