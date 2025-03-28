.. Aircraft Data Hierarchy documentation master file, created by
   sphinx-quickstart on Tue Apr 30 12:01:06 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Aircraft Data Hierarchy
===================================================

Description
-----------

The Aircraft Data Hierarchy (ADH) is a modern data definition standard for the aerospace vehicle design studies. The ADH enables engineers to exchange information (i.e. geometry, disciplinary tool inputs/outputs, requirements, etc.) between tools using a common data structure and a schema that can be validated. This structured system allows not only more efficient data transfer within an integrated workflow, but also improved collaboration between entities that utilize the ADH standard. The ADH is specifically architected to align the high-level needs of systems analysis (i.e., MDAO) and systems engineering (i.e., MBSE) including having a recursive structure. It includes modern programming features such as schema definition and validation using pydantic and support for JSON, YAML, and XML persistence files. Utility methods are being developed that will make the reading, writing, and manipulation of the ADH in python simple and straightforward.

Dependencies
------------

To use the ADH you need to use Python 3.8 or higher and Pydantic v2. 

The foundational structure of the ADH is provided by Pydantic v2 classes, ensuring a single source of data that is self-validating to manage the quality of the data. This approach makes the complexity of Aircraft Design in a Model-Based Systems Engineering (MBSE) environment more transparent and intuitive.


.. toctree::
   :maxdepth: 7
   :caption: Contents:

   reference/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
