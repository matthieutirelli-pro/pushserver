import json

import sseclient
import requests

from orm import Message


# Want to test for:
# * No messages are ever lost
# * messages go to the correct client
# * client only connected once


class TestMessage:
    def test_send(self, testapp, db):
        # minimal fields set
        res = testapp.post_json(
            "/message",
            {"body": "Message"},
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-A1"},
        )
        # everything set
        res = testapp.post_json(
            "/message",
            {"body": "Message", "priority": "HIGH", "subject": "subhect"},
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-A1"},
        )
        assert len(db.session.query(Message).all()) == 4
        # missing body
        res = testapp.post_json(
            "/message",
            {"priority": "HIGH", "subject": "subhect"},
            expect_errors=True,
            headers={"X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-A1"},
        )
        assert res.status_int == 400
        assert len(db.session.query(Message).all()) == 4

    def test_receive_stored(self, testserver, db):
        url = testserver.url + "/subscribe"
        res = requests.get(
            url,
            stream=True,
            headers={
                "X-Openpush-Key": "aaaaAAAAbbbbBBBB0000111-C1",
                "accept": "text/event-stream",
            },
        )
        client = sseclient.SSEClient(res.iter_content())
        m1 = json.loads(next(client.events()).data)
        m2 = json.loads(next(client.events()).data)
        client.close()
        assert m1["body"] == "Body1"
        assert m2["body"] == "Body2"
