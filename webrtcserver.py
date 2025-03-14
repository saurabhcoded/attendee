import asyncio
import json
import logging
from aiohttp import web
import aiohttp_cors
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.rtcrtpreceiver import RTCRtpReceiver
from aiortc.rtp import RtpPacket

logger = logging.getLogger("pc")
pcs = set()

async def offer(request):
    """
    Handle incoming SDP offers from the browser and return an SDP answer.
    """
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    # Instead of creating transceivers here, let's handle them in on_track
    print("DEBUG: Processing offer with following media sections:")
    for m_section in offer.sdp.split('\nm=')[1:]:
        media_type = m_section.split(' ')[0]
        print(f"Found media section: {media_type}")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "connected":
            print("DEBUG: Connection established, checking transceivers")
            for transceiver in pc.getTransceivers():
                print(f"Transceiver: mid={transceiver.mid}, direction={transceiver.direction}")
                print(f"Track state: {transceiver.receiver.track.readyState}")

    @pc.on("track")
    async def on_track(track):
        print(f"DEBUG: on_track called for {track.kind} track")
        print(f"Track details: kind={track.kind}, id={track.id}, readyState={track.readyState}")
        
        # Instead of creating a new transceiver, find or create one for this track
        transceivers = pc.getTransceivers()
        transceiver = next((t for t in transceivers if t.receiver.track == track), None)
        
        if not transceiver:
            print(f"DEBUG: No existing transceiver found for {track.kind}, creating new one")
            transceiver = pc.addTransceiver(track, direction="sendrecv")
        else:
            print(f"DEBUG: Found existing transceiver for {track.kind}")
            transceiver.direction = "sendrecv"
        
        print(f"DEBUG: Transceiver setup complete for {track.kind}")
        print(f"Transceiver details: mid={transceiver.mid}, direction={transceiver.direction}")
        
        # Add RTP packet handling
        @track.on("rtp")
        def on_rtp(packet: RtpPacket):
            print(f"DEBUG: Received RTP packet for {track.kind} track")
            print(f"  Sequence Number: {packet.sequence_number}")
            print(f"  Timestamp: {packet.timestamp}")
            print(f"  Payload Type: {packet.payload_type}")
            print(f"  SSRC: {packet.ssrc}")

        @track.on("ended")
        async def on_ended():
            print(f"DEBUG: Track {track.kind} ended")

        @track.on("started")
        async def on_started():
            print(f"DEBUG: Track {track.kind} started")

        print(f"DEBUG: Finished setting up handlers for {track.kind} track")

    # Handle the incoming offer
    await pc.setRemoteDescription(offer)

    # Create and set local answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    print(f"Sending answer: {pc.localDescription.sdp}")

    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    )

async def on_shutdown(app):
    # Close all peer connections on shutdown
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)

def main():
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    
    # Setup CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["POST", "OPTIONS"]
        )
    })
    
    # Add routes with CORS support
    resource = cors.add(app.router.add_resource("/offer"))
    cors.add(resource.add_route("POST", offer))
    
    app.on_shutdown.append(on_shutdown)

    # Run on http://localhost:8080
    web.run_app(app, port=8080)

if __name__ == "__main__":
    main()
