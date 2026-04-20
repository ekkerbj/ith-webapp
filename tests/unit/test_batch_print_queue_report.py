def test_batch_print_queue_route_embeds_selected_documents(app):
    response = app.test_client().get(
        "/reports/batch-print-queue"
        "?url=/reports/packing-list/7"
        "&url=/reports/ith-test-gauge-certificates/9"
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Batch Print Queue" in html
    assert "/reports/packing-list/7" in html
    assert "/reports/ith-test-gauge-certificates/9" in html
    assert html.count("<iframe") == 2
