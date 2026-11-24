import azure.functions as func


def test_registers_all_functions(function_app: func.FunctionApp) -> None:
    names = {f.get_function_name() for f in function_app.get_functions()}
    assert names == {"health", "hello"}
