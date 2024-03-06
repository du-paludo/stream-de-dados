# Data Stream Simulator
The goal of this project is to implement a UDP connection to transmit real-time data. In this project, we implemented both the client and server in Python. For data collection, we utilized the Open Meteo API, which provides real-time temperature information for a specific location based on the supplied latitude and longitude in the source code.

API link: <a href="https://api.open-meteo.com/v1/forecast">https://api.open-meteo.com/v1/forecast</a>

## Server
On the server side, the entire logic for storing and distributing data collected from the API was implemented. To enable communication with multiple clients, thread implementation was used for sending and receiving data simultaneously.

There are three threads on the server. One is responsible for listening on the specified port (5968) to check if any client wants to subscribe to the broadcast list. The second thread is responsible for sending packets to clients registered in the broadcast list. The third is responsible for receiving user input in case they wish to terminate the program.

The sent packets are the same for each client and contain only two fields: the sequence number of that packet in the stream and the temperature in Curitiba.

To terminate the server, simply type "exit" or "quit" on the command line. If the user wishes to change the interval between each sent packet, they can type "setinterval x," where x is the duration in seconds of the interval.

At the end of the server's execution, some statistics are displayed on the standard output, such as the total number of packets sent and the total number of connected clients.

## Client
When running the client program, the server's IP address is requested. After providing the IP address, an automatic subscription request message is sent to the server. Upon receiving the message, the server includes the client in the broadcast list, and the client starts receiving data sent by the server. These data (sequence number and temperature) are displayed on the standard output for each received packet.

The client checks the sequence number to determine if any packets were lost or if they arrived out of order. When the client wishes to cancel the subscription, they should type "unsubscribe" on the command line. Upon entering this command, a message is sent to the server, which removes the client from the broadcast list. Then, a report is displayed on the screen containing information about the received packets.

The concept of threads is also used in the client to simultaneously receive data from the server and read keyboard input.
