// Native async support using pyo3-async-runtimes with tokio
//
// This module provides truly async template rendering by using tokio's
// spawn_blocking for CPU-bound template rendering operations.

use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::{Arc, Mutex};

use minijinja::value::Value;

use crate::environment::{Environment, Inner};
use crate::typeconv::to_minijinja_value;

/// Render a template string asynchronously.
///
/// This function returns a Python awaitable that, when awaited, will render
/// the template string with the given context. The actual rendering is
/// performed in a tokio blocking task to avoid blocking the async runtime.
#[pyfunction]
#[pyo3(signature = (env, template, **context))]
pub fn render_str_async<'py>(
    py: Python<'py>,
    env: PyRef<'py, Environment>,
    template: String,
    context: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyAny>> {
    // Extract context from Python dict and convert to minijinja Values
    let ctx: Vec<(String, Value)> = match context {
        Some(dict) => {
            let mut values = Vec::new();
            for (key, value) in dict.iter() {
                let key_str: String = key.extract()?;
                let val = to_minijinja_value(&value);
                values.push((key_str, val));
            }
            values
        }
        None => Vec::new(),
    };

    // Clone the inner Arc for use in the async task
    let inner: Arc<Mutex<Inner>> = env.get_inner();

    // Get current event loop context - required for proper async operation
    let locals = pyo3_async_runtimes::tokio::get_current_locals(py)?;

    pyo3_async_runtimes::tokio::future_into_py_with_locals(py, locals, async move {
        // Use spawn_blocking for CPU-bound template rendering
        let result = tokio::task::spawn_blocking(move || {
            let guard = inner.lock().unwrap();
            let context_value: Value = ctx.into_iter().collect();
            guard.render_str_with_context(&template, context_value)
        })
        .await
        .map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Task join error: {}", e))
        })?;

        result.map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
    })
}

/// Render a named template asynchronously.
#[pyfunction]
#[pyo3(signature = (env, name, **context))]
pub fn render_template_async<'py>(
    py: Python<'py>,
    env: PyRef<'py, Environment>,
    name: String,
    context: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyAny>> {
    // Extract context from Python dict
    let ctx: Vec<(String, Value)> = match context {
        Some(dict) => {
            let mut values = Vec::new();
            for (key, value) in dict.iter() {
                let key_str: String = key.extract()?;
                let val = to_minijinja_value(&value);
                values.push((key_str, val));
            }
            values
        }
        None => Vec::new(),
    };

    let inner: Arc<Mutex<Inner>> = env.get_inner();

    // Get current event loop context - required for proper async operation
    let locals = pyo3_async_runtimes::tokio::get_current_locals(py)?;

    pyo3_async_runtimes::tokio::future_into_py_with_locals(py, locals, async move {
        let result = tokio::task::spawn_blocking(move || {
            let guard = inner.lock().unwrap();
            let context_value: Value = ctx.into_iter().collect();
            guard.render_template_with_context(&name, context_value)
        })
        .await
        .map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Task join error: {}", e))
        })?;

        result.map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
    })
}

/// Evaluate an expression asynchronously.
#[pyfunction]
#[pyo3(signature = (env, expr, **context))]
pub fn eval_expr_async<'py>(
    py: Python<'py>,
    env: PyRef<'py, Environment>,
    expr: String,
    context: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, PyAny>> {
    let ctx: Vec<(String, Value)> = match context {
        Some(dict) => {
            let mut values = Vec::new();
            for (key, value) in dict.iter() {
                let key_str: String = key.extract()?;
                let val = to_minijinja_value(&value);
                values.push((key_str, val));
            }
            values
        }
        None => Vec::new(),
    };

    let inner: Arc<Mutex<Inner>> = env.get_inner();

    // Get current event loop context - required for proper async operation
    let locals = pyo3_async_runtimes::tokio::get_current_locals(py)?;

    pyo3_async_runtimes::tokio::future_into_py_with_locals(py, locals, async move {
        let result = tokio::task::spawn_blocking(move || {
            let guard = inner.lock().unwrap();
            let context_value: Value = ctx.into_iter().collect();
            guard.eval_expression_with_context(&expr, context_value)
        })
        .await
        .map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Task join error: {}", e))
        })?;

        // Convert minijinja::Value to a serializable format
        result
            .map(|v| format!("{}", v))
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
    })
}
