import os

import pytest

import tests.util.open3e_cmd as open3e
from tests.util.dataset import dataset
from tests.util.wait import wait_for


DEFAULT_ECU = "0x680"
READ_DATASET_FILE = os.path.join(os.path.dirname(__file__), "test_data/read.json")


@pytest.mark.parametrize("ecu, did, expected", dataset(READ_DATASET_FILE).fixtures())
def test_read_cmd_json(ecu, did, expected):
    stdout, stderr = open3e.read(ecu, [did])

    assert "" == stderr
    assert str(expected) == stdout.strip()


def test_read_cmd_json_with_default_ecu():
    did = 256
    did_string = f"{did}"

    stdout, stderr = open3e.read_with_did_string(did_string)

    assert "" == stderr
    read_dataset = dataset(READ_DATASET_FILE)
    assert f"{read_dataset.get(DEFAULT_ECU, did)}" == stdout.splitlines()[0]


def test_read_cmd_json_with_named_ecu():
    ecu = "0x680"
    ecu_name = "0x680"
    did = 256
    did_string = f"{ecu_name}.{did}"

    stdout, stderr = open3e.read_with_did_string(did_string)

    assert "" == stderr
    read_dataset = dataset(READ_DATASET_FILE)
    assert f"{read_dataset.get(ecu, did)}" == stdout.splitlines()[0]


def test_read_cmd_json_multiple_dids_csv_format():
    ecu = "0x680"
    dids = [256, 505]

    stdout, stderr = open3e.read(ecu, dids)

    assert "" == stderr
    read_dataset = dataset(READ_DATASET_FILE)
    assert f"{dids[0]} {read_dataset.get(ecu, dids[0])}" == stdout.splitlines()[0]
    assert f"{dids[1]} {read_dataset.get(ecu, dids[1])}" == stdout.splitlines()[1]


def test_read_cmd_json_multiple_dids_csv_format_with_default_ecu():
    dids = [256, 505]
    did_string = f"{dids[0]},{dids[1]}"

    stdout, stderr = open3e.read_with_did_string(did_string)

    assert "" == stderr
    read_dataset = dataset(READ_DATASET_FILE)
    assert f"{dids[0]} {read_dataset.get(DEFAULT_ECU, dids[0])}" == stdout.splitlines()[0]
    assert f"{dids[1]} {read_dataset.get(DEFAULT_ECU, dids[1])}" == stdout.splitlines()[1]


def test_read_cmd_json_multiple_dids_list_format():
    ecu = "0x680"
    dids = [256, 505]
    did_string = f"{ecu}.[{dids[0]},{dids[1]}]"

    stdout, stderr = open3e.read_with_did_string(did_string)

    assert "" == stderr
    read_dataset = dataset(READ_DATASET_FILE)
    assert f"{dids[0]} {read_dataset.get(ecu, dids[0])}" == stdout.splitlines()[0]
    assert f"{dids[1]} {read_dataset.get(ecu, dids[1])}" == stdout.splitlines()[1]


def test_read_cmd_json_multiple_mixed_formats():
    hpmu_ecu = "0x680"
    hpmu_ecu_name = "0x680"
    hpmu_dids = [256, 262, 268, 381, 505]

    emcu_ecu = "0x6a1"
    emcu_ecu_name = "vitocharge"
    emcu_dids = [592, 604]
    did_string = f"{hpmu_dids[0]},{hpmu_ecu}.{hpmu_dids[1]},{hpmu_ecu}.[{hpmu_dids[2]},{hpmu_dids[3]}],{hpmu_ecu_name}.{hpmu_dids[4]},{emcu_ecu}.{emcu_dids[0]},{emcu_ecu_name}.{emcu_dids[1]}"

    stdout, stderr = open3e.read_with_did_string(did_string)

    assert "" == stderr
    read_dataset = dataset(READ_DATASET_FILE)
    assert f"{hpmu_dids[0]} {read_dataset.get(hpmu_ecu, hpmu_dids[0])}" == stdout.splitlines()[0]
    assert f"{hpmu_dids[1]} {read_dataset.get(hpmu_ecu, hpmu_dids[1])}" == stdout.splitlines()[1]
    assert f"{hpmu_dids[2]} {read_dataset.get(hpmu_ecu, hpmu_dids[2])}" == stdout.splitlines()[2]
    assert f"{hpmu_dids[3]} {read_dataset.get(hpmu_ecu, hpmu_dids[3])}" == stdout.splitlines()[3]
    assert f"{hpmu_dids[4]} {read_dataset.get(hpmu_ecu, hpmu_dids[4])}" == stdout.splitlines()[4]

    assert f"{emcu_dids[0]} {read_dataset.get(emcu_ecu, emcu_dids[0])}" == stdout.splitlines()[5]
    assert f"{emcu_dids[1]} {read_dataset.get(emcu_ecu, emcu_dids[1])}" == stdout.splitlines()[6]


def test_read_cmd_json_sub_did():
    ecu = "0x680"
    did = 256
    sub_did= "BusType"
    sub_did_fqn = f"{ecu}.{did}.{sub_did}"

    stdout, stderr = open3e.read_with_did_string(sub_did_fqn)

    assert "" == stderr
    read_dataset = dataset(READ_DATASET_FILE)
    assert str(read_dataset.get(ecu, did, sub_did)) == stdout.strip()


def test_read_cmd_raw():
    ecu = "0x680"
    did = 256

    stdout, stderr = open3e.read_raw(ecu, [did])

    assert "" == stderr
    assert '"01021f091400fd010109c000020064026500040031323334353637383031323334353637"' == stdout.strip()


@pytest.mark.parametrize("ecu, did, expected", dataset(READ_DATASET_FILE).fixtures())
def test_read_listen_json(open3e_mqtt_client, ecu, did, expected):
    with open3e.listen() as _:
        wait_for(lambda: open3e_mqtt_client.is_open3e_online())

        open3e_mqtt_client.subscribe(ecu, did)
        open3e_mqtt_client.publish_cmd("read-json", ecu, [did])

        wait_for(lambda: open3e_mqtt_client.received_messages_count() == 1)

        assert str(expected) == open3e_mqtt_client.received_message_payload(ecu, did)


def test_read_listen_json_multiple_dids(open3e_mqtt_client):
    ecu = "0x680"
    dids = [256, 507]

    with open3e.listen() as _:
        wait_for(lambda: open3e_mqtt_client.is_open3e_online())

        for did in dids:
            open3e_mqtt_client.subscribe(ecu, did)

        open3e_mqtt_client.publish_cmd("read-json", ecu, dids)

        wait_for(lambda: open3e_mqtt_client.received_messages_count() == 2)

        read_dataset = dataset(READ_DATASET_FILE)
        assert str(read_dataset.get(ecu, dids[0])) == open3e_mqtt_client.received_message_payload(ecu, dids[0])
        assert str(read_dataset.get(ecu, dids[1])) == open3e_mqtt_client.received_message_payload(ecu, dids[1])


def test_read_listen_json_sub_did(open3e_mqtt_client):
    ecu = "0x680"
    did = 256
    sub_did = "BusType"
    sub_did_fqn = f"{did}.{sub_did}"

    with open3e.listen() as _:
        wait_for(lambda: open3e_mqtt_client.is_open3e_online())

        # TODO: read sub did will be published under did root topic?
        open3e_mqtt_client.subscribe(ecu, did)
        open3e_mqtt_client.publish_cmd("read-json", ecu, [sub_did_fqn])

        wait_for(lambda: open3e_mqtt_client.received_messages_count() == 1)

        read_dataset = dataset(READ_DATASET_FILE)
        assert str(read_dataset.get(ecu, did, sub_did)) == open3e_mqtt_client.received_message_payload(ecu, did)


def test_read_listen_raw(open3e_mqtt_client):
    ecu = "0x680"
    did = 256

    with open3e.listen() as _:
        wait_for(lambda: open3e_mqtt_client.is_open3e_online())

        open3e_mqtt_client.subscribe(ecu, did)
        open3e_mqtt_client.publish_cmd("read-raw", ecu, [did])

        wait_for(lambda: open3e_mqtt_client.received_messages_count() == 1)

        assert "01021f091400fd010109c000020064026500040031323334353637383031323334353637" == open3e_mqtt_client.received_message_payload(ecu, did)

# mqtt topic per sub did
def test_read_listen(open3e_mqtt_client):
    ecu = "0x680"
    did = 256

    with open3e.listen() as _:
        wait_for(lambda: open3e_mqtt_client.is_open3e_online())

        # wildcard subscribe to all sub topics
        open3e_mqtt_client.subscribe(ecu, did, "/#")
        open3e_mqtt_client.publish_cmd("read", ecu, [did])

        wait_for(lambda: open3e_mqtt_client.received_messages_count() == 10)

        # TODO: verify each sub did topic? dataset structure with access to sub dids?
        assert "1" == open3e_mqtt_client.received_message_payload(ecu, did, "/BusAddress")
        assert "2" == open3e_mqtt_client.received_message_payload(ecu, did, "/BusType/ID")
        assert "1234567801234567" == open3e_mqtt_client.received_message_payload(ecu, did, "/VIN")
