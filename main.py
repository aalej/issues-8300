import os
import time
import itertools

from google.cloud import datastore
import concurrent.futures


def get_new_client():
    return datastore.Client(
        project=os.environ.get("GCLOUDC_PROJECT_ID", "demo-project"),
        namespace=None,
        _http=None,
    )


def sdk_increment_integer_entity(integer_pk):
    client = get_new_client()
    key = client.key("Integer", integer_pk)
    with client.transaction():
        entity = client.get(key=key)
        entity["value"] += 1
        client.put(entity)


def run_test():
    PORT = 10901
    os.environ["DATASTORE_EMULATOR_HOST"] = "127.0.0.1:%s" % PORT
    os.environ["DATASTORE_PROJECT_ID"] = "demo-project"

    initial_value = 0
    concurrent_writes = 10
    futures = []

    local_client = get_new_client()

    key = local_client.key("Integer", 1)
    entity = datastore.Entity(key)
    entity["value"] = initial_value
    local_client.put(entity)


    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_writes) as executor:
        for _ in range(concurrent_writes):
            futures.append(executor.submit(sdk_increment_integer_entity, 1))

    concurrent.futures.wait(futures)

    futures_exceptions = [future.exception() for future in futures]
    number_successful_writes = len(list(itertools.filterfalse(None, futures_exceptions)))
    if number_successful_writes == 0:
        print(futures_exceptions)
    else:
        print(f"All good, successful writes: {number_successful_writes}")

    from_db = local_client.get(key)

    assert number_successful_writes != 0
    assert from_db["value"] == number_successful_writes


def main():
    for i in range(1, 50):
        print("Run:", i)
        run_test()
        time.sleep(2)


if __name__ == "__main__":
    main()
