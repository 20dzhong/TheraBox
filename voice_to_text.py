import os
from dotenv import load_dotenv
import sounddevice as sd
import base64
import json
from text_to_voice import say_sum_shit

load_dotenv()

import websockets
import asyncio

URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"
AUTH_KEY = os.environ.get('ASSEMBLY_AI_KEY')
FRAMES_PER_BUFFER = 1600
MAX_BLANKS = 1
DEBUG = True

started = False
whole_message = ""
prev_result = ""
blanks = 0


async def send_receive(stream):
    if DEBUG:
        print(f'Connecting websocket to url ${URL}')
    async with websockets.connect(
            URL,
            extra_headers=(("Authorization", AUTH_KEY),),
            ping_interval=5,
            ping_timeout=20
    ) as _ws:
        await asyncio.sleep(0.1)
        await _ws.recv()

        async def send():
            while True:
                global blanks
                if blanks > MAX_BLANKS:
                    break
                try:
                    data = stream.read(FRAMES_PER_BUFFER)
                    buffer = b''.join(data[0])
                    data = base64.b64encode(buffer).decode("utf-8")
                    json_data = json.dumps({"audio_data": str(data)})
                    await _ws.send(json_data)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
                await asyncio.sleep(0.01)
            return True

        async def receive():
            while True:
                try:
                    result_str = await _ws.recv()
                    result = json.loads(result_str)['text']
                    global started
                    global whole_message
                    global blanks
                    global prev_result

                    if started == False and result != "":
                        started = True

                    if started == True and result == "":
                        blanks += 1
                        if blanks > MAX_BLANKS:
                            # print(f"Finished: {whole_message}")
                            return True
                    else:
                        blanks = 0

                    if len(prev_result) > len(result):
                        whole_message += prev_result + " "

                    # if DEBUG and started == True:
                    #     print(result)

                    prev_result = result

                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"

        say_sum_shit("I'm listening")
        send_result, receive_result = await asyncio.gather(send(), receive())


def cop_speech():
    global started
    global whole_message
    global prev_result
    global blanks
    started = False
    whole_message = ""
    prev_result = ""
    blanks = 0

    stream = sd.InputStream(samplerate=16000, blocksize=FRAMES_PER_BUFFER, channels=1, dtype='int16')
    stream.start()
    asyncio.run(send_receive(stream))
    stream.stop()
    return whole_message


# while True:
#     input("Press Enter to continue...")
#     print(cop_speech())
