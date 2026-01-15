use pyo3::prelude::*;
use pyo3::types::PyBytes;

mod async_native;
mod environment;
mod error_support;
mod fast_conv;
mod state;
mod typeconv;

/// Check if orjson is available for fast JSON serialization
#[pyfunction]
fn has_orjson(py: Python<'_>) -> bool {
    fast_conv::is_orjson_available(py)
}

/// Check if pydantic is available for type-safe models
#[pyfunction]
fn has_pydantic(py: Python<'_>) -> bool {
    fast_conv::is_pydantic_available(py)
}

/// Serialize a Python object to JSON bytes using orjson if available
/// Falls back to returning None if orjson is not installed
#[pyfunction]
fn orjson_dumps<'py>(py: Python<'py>, obj: &Bound<'py, PyAny>) -> Option<Bound<'py, PyBytes>> {
    fast_conv::orjson_serialize(py, obj).map(|bytes| PyBytes::new(py, &bytes))
}

/// Deserialize JSON bytes to a Python object using orjson if available
/// Falls back to returning None if orjson is not installed
#[pyfunction]
fn orjson_loads<'py>(py: Python<'py>, data: &[u8]) -> Option<Bound<'py, PyAny>> {
    fast_conv::orjson_deserialize(py, data)
}

/// Validate a dict/context against a Pydantic model class
/// Returns the validated model instance or raises ValidationError
#[pyfunction]
fn validate_context<'py>(
    py: Python<'py>,
    model_class: &Bound<'py, PyAny>,
    data: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    fast_conv::validate_context(py, model_class, data)
}

#[pymodule(gil_used = false)]
fn _lowlevel(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<environment::Environment>()?;
    m.add_class::<state::StateRef>()?;
    m.add_class::<error_support::ErrorInfo>()?;
    m.add_function(wrap_pyfunction!(error_support::get_panic_info, m)?)?;
    m.add_function(wrap_pyfunction!(has_orjson, m)?)?;
    m.add_function(wrap_pyfunction!(has_pydantic, m)?)?;
    m.add_function(wrap_pyfunction!(orjson_dumps, m)?)?;
    m.add_function(wrap_pyfunction!(orjson_loads, m)?)?;
    m.add_function(wrap_pyfunction!(validate_context, m)?)?;
    // Native async functions
    m.add_function(wrap_pyfunction!(async_native::render_str_async, m)?)?;
    m.add_function(wrap_pyfunction!(async_native::render_template_async, m)?)?;
    m.add_function(wrap_pyfunction!(async_native::eval_expr_async, m)?)?;
    crate::error_support::init_panic_hook();
    Ok(())
}
