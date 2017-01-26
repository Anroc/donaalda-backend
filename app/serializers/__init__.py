"""This package contains the various serializers used throughout this
application.

It is divided into three parts:
    - v1 which contains the DRF modelSerializers used to prepare our database
      models for the api. It is called that because the api endpoints that
      purely query the database are listed under `/v1/`,
    - matching which contains serializers and data strucutres that are used to
      parse and validate the input filters for the matching algorithm, and
    - utils which contains various custom serializers and fields.
"""
