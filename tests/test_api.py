'''
import requests
import time
import os
import sys

# URL of your Flask API
API_URL = "http://localhost:8080"


def running_time_counter():
    start_time = time.time()

    try:
        while True:
            elapsed_time = time.time() - start_time
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Clear the screen (works in UNIX, macOS, Windows)
            os.system('cls' if os.name == 'nt' else 'clear')

            # Print the elapsed time. Using '\r' to return the cursor to the start of the line
            sys.stdout.write("\rElapsed Time: {:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds)))
            sys.stdout.flush()

            # Wait a bit before updating the screen
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nTimer stopped.")
        sys.exit(0)

# Test the /start endpoint
start_response = requests.get(f"{API_URL}/start")
if start_response.status_code == 200:
    print("Start Conversation:", start_response.json())
    thread_id = start_response.json()['thread_id']

    message = input()


    while message != "-1":

        # Test the /chat endpoint with an example message
        chat_payload = {
            "thread_id": thread_id,
            "message": message
        }
        chat_response = requests.post(f"{API_URL}/chat", json=chat_payload)
        if chat_response.status_code == 200:
            print(chat_response.json()['response'])

            message = input()
        else:
            print("Error in Chat Response:", chat_response.status_code, chat_response.text)
            break
else:
    print("Error in Start Conversation:", start_response.status_code, start_response.text)

'''


import asyncio
import aiohttp
import time
import os
import sys

API_URL = "http://localhost:8080"

async def running_time_counter(start_time):
    '''
    while True:
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        #sys.stdout.write(f"\rElapsed Time: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
        sys.stdout.write(f"\rElapsed Time: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
        sys.stdout.flush()
        await asyncio.sleep(0.1)  # Run this every 0.1 seconds
    '''

    while True:
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(elapsed_time, 60)
        hundredths = (elapsed_time - int(elapsed_time)) * 100  # Calculate hundredths of a second

        # Format the time string with minutes, seconds, and hundredths of a second
        time_str = f"\rElapsed Time: {int(minutes):02}:{int(seconds):02}.{int(hundredths):02}"
        sys.stdout.write(time_str)
        sys.stdout.flush()
        await asyncio.sleep(0.01)  # Update every 0.01 seconds for smoother hundredths count

async def main():
    async with aiohttp.ClientSession() as session:
        # Start the conversation
        async with session.get(f"{API_URL}/start") as response:
            if response.status == 200:
                data = await response.json()
                print("Start Conversation:", data)
                thread_id = data['thread_id']
            else:
                print("Error in Start Conversation:", response.status)
                return

        while True:
            message = input("\n")
            if message == "-1":
                break

            # Send message and start timer
            start_time = time.time()
            timer_task = asyncio.create_task(running_time_counter(start_time))

            chat_payload = {"thread_id": thread_id, "message": message}
            async with session.post(f"{API_URL}/chat", json=chat_payload) as chat_response:
                if chat_response.status == 200:
                    response_data = await chat_response.json()
                    #print("\n",response_data['response'])
                    print(f"\n{response_data['response']}")

                else:
                    print("\n", chat_response.status)

            # Stop the timer
            timer_task.cancel()
            try:
                await timer_task
            except asyncio.CancelledError:
                pass

asyncio.run(main())

