// Fast serialization module using orjson and pydantic integration
//
// This module provides high-performance JSON serialization by calling orjson
// from Rust via PyO3, and Pydantic model support for type-safe templates.

use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyBytes, PyDict, PyList, PyTuple};

use minijinja::value::Value;

use crate::typeconv::DynamicObject;

// Cached references to Python modules and functions
static ORJSON_DUMPS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static ORJSON_LOADS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static PYDANTIC_BASEMODEL: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

/// Initialize orjson.dumps function reference
fn get_orjson_dumps(py: Python<'_>) -> PyResult<&Py<PyAny>> {
    ORJSON_DUMPS.get_or_try_init::<_, PyErr>(py, || {
        let orjson = py.import("orjson")?;
        Ok(orjson.getattr("dumps")?.into())
    })
}

/// Initialize orjson.loads function reference
fn get_orjson_loads(py: Python<'_>) -> PyResult<&Py<PyAny>> {
    ORJSON_LOADS.get_or_try_init::<_, PyErr>(py, || {
        let orjson = py.import("orjson")?;
        Ok(orjson.getattr("loads")?.into())
    })
}

/// Get pydantic.BaseModel class reference
fn get_pydantic_basemodel(py: Python<'_>) -> PyResult<&Py<PyAny>> {
    PYDANTIC_BASEMODEL.get_or_try_init::<_, PyErr>(py, || {
        let pydantic = py.import("pydantic")?;
        Ok(pydantic.getattr("BaseModel")?.into())
    })
}

/// Check if a Python object is a Pydantic BaseModel instance
pub fn is_pydantic_model(py: Python<'_>, obj: &Bound<'_, PyAny>) -> bool {
    match get_pydantic_basemodel(py) {
        Ok(basemodel) => obj.is_instance(basemodel.bind(py)).unwrap_or(false),
        Err(_) => false, // pydantic not installed
    }
}

/// Convert a Pydantic model to a dictionary using model_dump()
pub fn pydantic_model_to_dict<'py>(
    _py: Python<'py>,
    model: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyDict>> {
    let dict = model.call_method0("model_dump")?;
    dict.extract::<Bound<'py, PyDict>>().map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
            "model_dump() did not return a dict: {}",
            e
        ))
    })
}

/// Serialize a Python object to JSON bytes using orjson
/// Returns None if orjson is not available or serialization fails
pub fn orjson_serialize(py: Python<'_>, obj: &Bound<'_, PyAny>) -> Option<Vec<u8>> {
    let dumps = get_orjson_dumps(py).ok()?;
    let result = dumps.call1(py, (obj,)).ok()?;
    let bytes: Bound<'_, PyBytes> = result.bind(py).extract().ok()?;
    Some(bytes.as_bytes().to_vec())
}

/// Deserialize JSON bytes to a Python object using orjson
/// Returns None if orjson is not available or deserialization fails
pub fn orjson_deserialize<'py>(py: Python<'py>, data: &[u8]) -> Option<Bound<'py, PyAny>> {
    let loads = get_orjson_loads(py).ok()?;
    let bytes = PyBytes::new(py, data);
    loads.call1(py, (bytes,)).ok().map(|r| r.into_bound(py))
}

/// Convert a Pydantic model to a MiniJinja Value
/// This extracts the model data as a dictionary and converts it
pub fn pydantic_to_value(py: Python<'_>, model: &Bound<'_, PyAny>) -> Value {
    match pydantic_model_to_dict(py, model) {
        Ok(dict) => dict_to_value(py, &dict),
        Err(_) => Value::from_object(DynamicObject::new(model.clone().unbind())),
    }
}

/// Convert a Python dict to MiniJinja Value
/// Uses Value's FromIterator implementation for maps
fn dict_to_value(py: Python<'_>, dict: &Bound<'_, PyDict>) -> Value {
    // Collect key-value pairs and create a map Value using FromIterator
    let pairs: Vec<(String, Value)> = dict
        .iter()
        .filter_map(|(key, val)| {
            key.extract::<String>()
                .ok()
                .map(|k| (k, python_to_value(py, &val)))
        })
        .collect();

    // Value implements FromIterator for map-like structures
    pairs.into_iter().collect()
}

/// Convert a Python list to MiniJinja Value
fn list_to_value(py: Python<'_>, list: &Bound<'_, PyList>) -> Value {
    let values: Vec<Value> = list.iter().map(|item| python_to_value(py, &item)).collect();
    Value::from(values)
}

/// Fast Python to MiniJinja Value conversion
/// Uses type checking to convert common types efficiently
pub fn python_to_value(py: Python<'_>, obj: &Bound<'_, PyAny>) -> Value {
    // None
    if obj.is_none() {
        return Value::from(());
    }

    // Bool (must check before int, as bool is subclass of int in Python)
    if let Ok(val) = obj.extract::<bool>() {
        return Value::from(val);
    }

    // Integer
    if let Ok(val) = obj.extract::<i64>() {
        return Value::from(val);
    }

    // Handle large integers that exceed i64
    if let Ok(val) = obj.extract::<i128>() {
        // Convert to string to avoid precision loss
        return Value::from(val.to_string());
    }

    // Float
    if let Ok(val) = obj.extract::<f64>() {
        return Value::from(val);
    }

    // String
    if let Ok(val) = obj.extract::<String>() {
        // Check for __html__ method (safe string)
        if let Ok(to_html) = obj.getattr("__html__") {
            if to_html.is_callable() {
                if let Ok(html) = to_html.call0() {
                    if let Ok(html_str) = html.extract::<String>() {
                        return Value::from_safe_string(html_str);
                    }
                }
            }
        }
        return Value::from(val);
    }

    // Pydantic model
    if is_pydantic_model(py, obj) {
        return pydantic_to_value(py, obj);
    }

    // Dict
    if let Ok(dict) = obj.extract::<Bound<'_, PyDict>>() {
        return dict_to_value(py, &dict);
    }

    // List
    if let Ok(list) = obj.extract::<Bound<'_, PyList>>() {
        return list_to_value(py, &list);
    }

    // Tuple (convert to list in MiniJinja)
    if let Ok(tuple) = obj.extract::<Bound<'_, PyTuple>>() {
        let values: Vec<Value> = tuple
            .iter()
            .map(|item| python_to_value(py, &item))
            .collect();
        return Value::from(values);
    }

    // Fallback to DynamicObject wrapper
    Value::from_object(DynamicObject::new(obj.clone().unbind()))
}

/// Check if orjson is available
pub fn is_orjson_available(py: Python<'_>) -> bool {
    get_orjson_dumps(py).is_ok()
}

/// Check if pydantic is available
pub fn is_pydantic_available(py: Python<'_>) -> bool {
    get_pydantic_basemodel(py).is_ok()
}

/// Validate a dict against a Pydantic model class
/// Returns the validated model instance or raises ValidationError
pub fn validate_context<'py>(
    _py: Python<'py>,
    model_class: &Bound<'py, PyAny>,
    data: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    // Call model_class.model_validate(data) for Pydantic v2
    model_class.call_method1("model_validate", (data,))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_orjson_availability() {
        Python::attach(|py| {
            // This test just checks the function doesn't panic
            let _ = is_orjson_available(py);
        });
    }

    #[test]
    fn test_pydantic_availability() {
        Python::attach(|py| {
            // This test just checks the function doesn't panic
            let _ = is_pydantic_available(py);
        });
    }
}
