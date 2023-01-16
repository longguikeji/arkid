# Plug -in base class

The most basic base class of plug -in **arkid.core.extension.Extension**

The core method of supporting hot insertion is **start()** and **stop()**
Will call**load()**and**unload()**method，These two methods are in each plug -in subclass，Use the operation of installation and uninstallation

* **load()** Abstract method，It is required that each plug -in should be realized。
* **unload()** Can also be reloaded。Will all registered APIs registered in the process of load ()，event，Wait for destruction。

therefore，Try to avoid directly using the kernel API in the plug -in，And to be encapsulated in the plug -in **register** Starting method。transfer register When the type of method，The destruction of related operations will be executed in STOP，No need to do it in Unload。

Some changes to the page content，For example, Actions related modifications，The destruction displayed in Unload。

!!! hint
    In fact，Call**start()**The presence will be carried out **migrate**，yes！Plug -in migrations Still effective。


::: arkid.core.extension.Extension
::: arkid.core.extension.create_extension_schema
::: arkid.core.extension.create_extension_schema_by_package
::: arkid.core.extension.create_extension_schema_from_django_model
