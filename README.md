# Repro for issue 8300

## Versions

firebase-tools: v13.33.0<br>
python: Python 3.12.4<br>

```
Google Cloud SDK 514.0.0
beta 2025.03.07
bq 2.1.14
cloud-datastore-emulator 2.3.1
cloud-firestore-emulator 1.19.9
core 2025.03.07
gcloud-crc32c 1.0.0
gsutil 5.33
```

## Steps to reproduce

1. Run `python3.12 -m venv venv`
1. Run `. venv/bin/activate` to activate the venv
1. Run `python3.12 -m pip install -r requirements.txt` to install dependencies
1. On a separate terminal, satrt the emulator by running `gcloud emulators firestore start --host-port=127.0.0.1:10901 --database-mode=datastore-mode`
1. Run `python3.12 main.py`

```
Run: 1
[Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.')]
Traceback (most recent call last):
  File "/Users/USER/Desktop/firebase-tools/issues/8300/main.py", line 70, in <module>
    main()
  File "/Users/USER/Desktop/firebase-tools/issues/8300/main.py", line 65, in main
    run_test()
  File "/Users/USER/Desktop/firebase-tools/issues/8300/main.py", line 58, in run_test
    assert number_successful_writes != 0
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
```

Note: often the error occurs on the first run, rarely on the second.

```
Run: 1
All good, successful writes: 1
Run: 2
[Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.'), Aborted('Transaction lock timeout.')]
Traceback (most recent call last):
  File "/Users/USER/Desktop/firebase-tools/issues/8300/main.py", line 70, in <module>
    main()
  File "/Users/USER/Desktop/firebase-tools/issues/8300/main.py", line 65, in main
    run_test()
  File "/Users/USER/Desktop/firebase-tools/issues/8300/main.py", line 58, in run_test
    assert number_successful_writes != 0
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError
```

## Connecting to actual project

When connecting to an actual project, no errors are raised

1. Run `export GOOGLE_APPLICATION_CREDENTIALS=./service-account.json`
2. Update the Python code to something like below:

```python
import os
import time
import itertools

from google.cloud import datastore
import concurrent.futures


def get_new_client():
    return datastore.Client(
        project=os.environ.get("GCLOUDC_PROJECT_ID", "PROJECT_ID"),
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
    # os.environ["DATASTORE_EMULATOR_HOST"] = "127.0.0.1:%s" % PORT
    os.environ["DATASTORE_PROJECT_ID"] = "PROJECT_ID"

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
```

Ouputs no errors, completes all runs

```
Run: 1
All good, successful writes: 3
Run: 2
All good, successful writes: 2
Run: 3
All good, successful writes: 2
Run: 4
All good, successful writes: 2
Run: 5
All good, successful writes: 3
Run: 6
All good, successful writes: 2
Run: 7
All good, successful writes: 2
Run: 8
All good, successful writes: 2
Run: 9
All good, successful writes: 2
Run: 10
All good, successful writes: 2
Run: 11
All good, successful writes: 3
Run: 12
All good, successful writes: 2
Run: 13
All good, successful writes: 2
Run: 14
All good, successful writes: 2
Run: 15
All good, successful writes: 2
Run: 16
All good, successful writes: 2
Run: 17
All good, successful writes: 2
Run: 18
All good, successful writes: 2
Run: 19
All good, successful writes: 2
Run: 20
All good, successful writes: 2
Run: 21
All good, successful writes: 2
Run: 22
All good, successful writes: 2
Run: 23
All good, successful writes: 2
Run: 24
All good, successful writes: 2
Run: 25
All good, successful writes: 3
Run: 26
All good, successful writes: 2
Run: 27
All good, successful writes: 3
Run: 28
All good, successful writes: 2
Run: 29
All good, successful writes: 2
Run: 30
All good, successful writes: 2
Run: 31
All good, successful writes: 3
Run: 32
All good, successful writes: 3
Run: 33
All good, successful writes: 2
Run: 34
All good, successful writes: 1
Run: 35
All good, successful writes: 2
Run: 36
All good, successful writes: 2
Run: 37
All good, successful writes: 2
Run: 38
All good, successful writes: 3
Run: 39
All good, successful writes: 2
Run: 40
All good, successful writes: 2
Run: 41
All good, successful writes: 3
Run: 42
All good, successful writes: 2
Run: 43
All good, successful writes: 2
Run: 44
All good, successful writes: 1
Run: 45
All good, successful writes: 1
Run: 46
All good, successful writes: 2
Run: 47
All good, successful writes: 2
Run: 48
All good, successful writes: 3
Run: 49
All good, successful writes: 2
```
