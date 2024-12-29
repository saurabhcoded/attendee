import asyncio
import os
import subprocess
import click
import datetime
import requests
import json

from time import sleep

import undetected_chromedriver as uc

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

async def join_meet():
    meet_link = os.getenv("GMEET_LINK", "https://meet.google.com/sam-ptgk-ppm")
    print(f"start recorder for {meet_link}")

    options = uc.ChromeOptions()

    options.add_argument("--use-fake-ui-for-media-stream")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    # options.add_argument('--headless=new')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    log_path = "chromedriver.log"

    driver = uc.Chrome(service_log_path=log_path, use_subprocess=False, options=options)

    driver.set_window_size(1920, 1080)

    # Add your JavaScript code before loading the page

    js_code = """

class WebRtcProxy {
    constructor(config) {
        this.state = {
            peerMessages: [],
            logChannelArgs: true,
            channelListeners: []
        };
        this.config = config;
    }

    initialize() {
        if (!window.RTCPeerConnection) {
            return false;
        }

        if (!window.ff_channels) {
            window.ff_channels = {};
        }

        const OriginalRTCPeerConnection = window.RTCPeerConnection;
        const originalCreateDataChannel = OriginalRTCPeerConnection.prototype.createDataChannel;
        const state = this.state;  // Capture state in closure

        if (originalCreateDataChannel) {
            OriginalRTCPeerConnection.prototype.createDataChannel = function() {
                if (state.logChannelArgs) {
                    console.log("creating channel args", arguments);
                }

                try {
                    const channel = originalCreateDataChannel.apply(this, arguments);
                    console.log('channel', channel)
                    console.log('state.channelListeners', state.channelListeners)
                    //channel.addEventListener("message", (event) => {
                    //    console.log('event', event)
                    //});
                    if (channel && state.channelListeners.length > 0) {
                        const matchingListener = state.channelListeners.find(
                            listener => listener.label === channel.label
                        );

                        console.log('matchingListener', matchingListener, 'channel', channel.label)

                        if (matchingListener) {
                            channel.addEventListener("message", matchingListener.callback);
                            
                            if (matchingListener.monitor) {
                                matchingListener.monitor(channel);
                            }
                        }

                        window.ff_channels[channel.label] = channel;
                    }

                    return channel;
                } catch (error) {
                    console.log(error);
                }
            };
        }

        // Capture config in closure
        const config = this.config;

        window.RTCPeerConnection = function(configuration, constraints) {
            const peerConnection = new OriginalRTCPeerConnection(configuration, constraints);
            
            if (config && config.debug) {
                console.log("created peer connection", peerConnection);
            }

            // Use captured state instead of this.state
            for (const message of state.peerMessages) {
                peerConnection.addEventListener(message.event, (event) => {
                    message.callback(peerConnection, event);
                });
            }

            return peerConnection;
        };

        window.RTCPeerConnection.prototype = OriginalRTCPeerConnection.prototype;
        
        return true;
    }

    register(options) {
        this.state.peerMessages.push(...options.peerMessages);
        this.state.logChannelArgs = options.logChannelArgs;
        this.state.channelListeners.push(...options.channelListeners);
        console.log('register', this.state)
    }
}
const monitorCaptionsChannel = (channel) => {
    console.log('monitorCaptionsChannel', channel)
}

const handleCaptionMessage = (event) => {
    console.log('handleCaptionMessage', event)
}

const handleDataChannel = (peerConnection, event) => {
    if (event.channel.label === "collections") {
        window.proxyPeerConnection = peerConnection;
        
        if (debug) {
            console.log("data channel message: ", event);
        }
        
        event.channel.addEventListener("message", handleCollectionMessage);
    }
};

const handleTrack = (t) => {
    console.log('handleTrack', t)
}

const peerConnectionProxy = new WebRtcProxy({debug: true});
const proxyStatus = peerConnectionProxy.initialize();
peerConnectionProxy.register({
    logChannelArgs: false,
    peerMessages: [
        { event: "datachannel", callback: handleDataChannel },
        { event: "track", callback: handleTrack }
    ],
    channelListeners: [
        { 
            label: "captions", 
            callback: handleCaptionMessage,
            monitor: monitorCaptionsChannel 
        }
    ]
});
    """

    js_code_old2 = """
/*
"use strict";

const { XhrProxy } = require("../proxies");
const { unzip } = require("../lib/utils");
const { CollectionMessage, CaptionWrapper, MeetingSpaceCollectionResponse, ChatData, ResolveMeeting } = require("../decoder/decoder");
const { START_AUDIO_ID, WEB_STENOGRAPHER_ERROR, WEB_STENOGRAPHER_LOG } = require("../constants/default");
const { DefaultNotifier } = require("../components/notifier");
*/

class WebRtcProxy {
    constructor(config) {
        console.log('WebRtcProxy constructor', config)
        this.state = {
            peerMessages: [],
            logChannelArgs: false,
            channelListeners: []
        };
    }

    initialize() {
        this.state = {
            peerMessages: [],
            logChannelArgs: false,
            channelListeners: []
        };

        // Check if WebRTC is supported
        if (!window.RTCPeerConnection) {
            return false;
        }

        // Initialize channels container if not exists
        if (!window.ff_channels) {
            window.ff_channels = {};
        }

        const OriginalRTCPeerConnection = window.RTCPeerConnection;
        const originalCreateDataChannel = OriginalRTCPeerConnection.prototype.createDataChannel;

        // Only proceed if createDataChannel exists
        if (originalCreateDataChannel) {
            // Override createDataChannel method
            OriginalRTCPeerConnection.prototype.createDataChannel = function() {
                if (this.state.logChannelArgs) {
                    console.log("creating channel args", arguments);
                }

                try {
                    const channel = originalCreateDataChannel.apply(this, arguments);
                    
                    if (channel && this.state.channelListeners.length > 0) {
                        const matchingListener = this.state.channelListeners.find(
                            listener => listener.label === channel.label
                        );

                        if (matchingListener) {
                            channel.addEventListener("message", matchingListener.callback);
                            
                            if (matchingListener.monitor) {
                                matchingListener.monitor(channel);
                            }
                        }

                        window.ff_channels[channel.label] = channel;
                    }

                    return channel;
                } catch (error) {
                    console.log(error);
                }
            };
        }

        // Store reference to 'this' for use in constructor
        const self = this;

        // Override RTCPeerConnection constructor
        window.RTCPeerConnection = function(configuration, constraints) {
            const peerConnection = new OriginalRTCPeerConnection(configuration, constraints);
            
            if (true) {
                console.log("created peer connection", peerConnection);
            }
            console.log('state:', self.state);

            // Add event listeners from peerMessages
            for (const message of self.state.peerMessages) {
                peerConnection.addEventListener(message.event, (event) => {
                    message.callback(peerConnection, event);
                });
            }

            return peerConnection;
        };

        // Maintain prototype chain
        window.RTCPeerConnection.prototype = OriginalRTCPeerConnection.prototype;
        
        return true;
    }

    register(options) {
        // Update state with new options
        this.state.peerMessages.push(...options.peerMessages);
        this.state.logChannelArgs = options.logChannelArgs;
        this.state.channelListeners.push(...options.channelListeners);
    }
}

/**
 * Google Meets functionality handler
 * @param {Map} userMap - Map to store user details
 * @param {Map} captionsMap - Map to store captions
 * @param {Map} audioChunksMap - Map to store audio chunks
 * @param {Map} chatMessagesMap - Map to store chat messages
 * @param {Object} peerConnectionProxy - WebRTC peer connection proxy
 * @param {Object} fetchProxy - Fetch request proxy
 * @param {Object} rtcProxy - RTC functionality proxy
 * @param {boolean} debug - Enable debug logging
 */
GoogleMeets = (userMap, captionsMap, audioChunksMap, chatMessagesMap, peerConnectionProxy, fetchProxy, rtcProxy, debug = false) => {
    // Internal state
    let audioDestination;
    let mediaRecorder;
    let dataChannelId = 2643;
    let isCaptionsServiceStopped = false;
    let captionsChannel = null;
    let currentAudioId = START_AUDIO_ID;
    let audioContext = null;

    // Collections
    const audioStreams = [];
    const lastMessageIds = new Map();
    const xhrProxy = XhrProxy();
    let calendarMetadata = null;
    let meetingMetadata = null;
    const htmlAudioStreams = [];

    // Initialize notifier for error handling
    const notifier = DefaultNotifier();

    /**
     * Handles collection messages containing user and chat data
     */
    const handleCollectionMessage = (event) => {
        if (debug) {
            console.log("collection message: ", event);
        }

        const unzippedData = unzip(event.data);
        const message = CollectionMessage.decode(unzippedData);

        if (!message.body?.wrapper?.wrapper) {
            return;
        }

        // Handle chat messages
        if (message.body.wrapper.wrapper.chat) {
            const chatMessages = message.body.wrapper.wrapper.chat;
            for (const chat of chatMessages) {
                const user = userMap.get(chat.body.deviceId);
                chatMessagesMap.set(chat.body.messageId, {
                    ...chat.body,
                    user: {
                        name: user?.name || "",
                        fullName: user?.fullName || "",
                        image: user?.image || "",
                        id: user?.id || ""
                    }
                });
            }
        }

        // Handle user details
        if (message.body.wrapper.wrapper.wrapper?.userDetails) {
            const users = message.body.wrapper.wrapper.wrapper.userDetails;
            for (const user of users) {
                userMap.set(user.deviceId, {
                    id: user.deviceId,
                    name: user.name,
                    fullName: user.fullName,
                    image: user.profile
                });
            }
        }
    };

    /**
     * Handles data channel setup for captions
     */
    const handleDataChannel = (peerConnection, event) => {
        if (event.channel.label === "collections") {
            window.proxyPeerConnection = peerConnection;
            
            if (debug) {
                console.log("data channel message: ", event);
            }
            
            event.channel.addEventListener("message", handleCollectionMessage);
        }
    };

    // Caption handling logic
    let nextCaptionId = 65110;
    const captionIds = [];
    const captionMap = new Map();

    /**
     * Processes caption data from the WebRTC data channel
     */
    const handleCaptionMessage = (event) => {
        try {
            const unzippedData = unzip(event.data);
            const wrapper = CaptionWrapper.decode(unzippedData);

            if (wrapper.unknown !== "") {
                console.log("unknown data found: ", Buffer.from(unzippedData).toString('hex'));
                return;
            }

            // Manage caption ID cache
            if (captionIds.length > 50) {
                const oldestId = captionIds.shift();
                captionMap.delete(oldestId);
            }

            const captionKey = `${wrapper.caption.captionId}/${wrapper.caption.deviceSpace}`;
            let messageId = captionMap.get(captionKey);

            if (!messageId) {
                messageId = nextCaptionId++;
                captionIds.push(captionKey);
                captionMap.set(captionKey, messageId);
            }

            const existingCaption = captionsMap.has(messageId);
            const user = userMap.get(wrapper.caption.deviceSpace);
            const lastMessageId = lastMessageIds.get(user.id) || -1;

            if (messageId > lastMessageId) {
                lastMessageIds.set(user.id, messageId);
            }

            let captionData;
            if (existingCaption) {
                const existing = captionsMap.get(messageId);
                let endTimestamp = Date.now();
                
                if (existing.messageId < lastMessageId) {
                    endTimestamp = existing.endTs;
                }

                captionData = {
                    ...existing,
                    endTs: endTimestamp,
                    caption: wrapper.caption.caption,
                    sequence: wrapper.caption.version,
                    updatedAt: Date.now()
                };
            } else {
                captionData = {
                    messageId,
                    receivedCaptionId: wrapper.caption.captionId,
                    caption: wrapper.caption.caption,
                    sequence: wrapper.caption.version,
                    firstReceiveTs: Date.now(),
                    updatedAt: Date.now(),
                    endTs: Date.now(),
                    user: {
                        id: user.id,
                        name: user.name,
                        fullName: user.fullName,
                        image: user.image
                    }
                };
            }

            captionsMap.set(wrapper.caption.captionId, captionData);
        } catch (error) {
            console.log(error);
            const errorDetails = `${error.message} ${error.stack.substring(0, 1000)}`;
            notifier.notify(WEB_STENOGRAPHER_ERROR, "CaptionMessage " + errorDetails);
        }
    };

    // Additional methods for meeting space data, audio handling, etc.
    
    /**
     * Initialize all required proxies and event listeners
     */
    const initialize = () => {
        try {
            // Initialize RTC proxy
            rtcProxy.initialize();
            rtcProxy.register({
                onReplaceTrack: handleTrackReplacement
            });

            // Initialize peer connection proxy
            const proxyStatus = peerConnectionProxy.initialize();
            peerConnectionProxy.register({
                logChannelArgs: false,
                peerMessages: [
                    { event: "datachannel", callback: handleDataChannel },
                    { event: "track", callback: handleTrack }
                ],
                channelListeners: [
                    { 
                        label: "captions", 
                        callback: handleCaptionMessage,
                        monitor: monitorCaptionsChannel 
                    }
                ]
            });

            // Set proxy status metadata
            const metaElement = document.createElement("meta");
            metaElement.setAttribute("id", "ff-proxy-check");
            metaElement.setAttribute("name", "hasCreatedProxies");
            metaElement.setAttribute("content", String(proxyStatus));
            (document.head || document.documentElement).prepend(metaElement);

            // Initialize audio context
            window.addEventListener("load", () => {
                notifier.notify(WEB_STENOGRAPHER_LOG, "Audio::window load event");
                audioContext = new AudioContext();
                window.ff_audio_context = audioContext;
            });

            // Initialize fetch proxy
            initializeFetchProxy();
            
            // Initialize XHR proxy
            initializeXhrProxy();

        } catch (error) {
            const errorDetails = `${error.message} ${error.stack.substring(0, 1000)}`;
            notifier.notify(WEB_STENOGRAPHER_ERROR, "initializer failed with: " + errorDetails);
        }
    };

    return {
        initialize,
        startCaptionsService: startCaptionsService,
        stopCaptionsService: stopCaptionsService,
        startRecorder: startRecorder,
        stopRecorder: stopRecorder,
        getMetadata: getMetadata
    };
};

const monitorCaptionsChannel = (channel) => {
    console.log('monitorCaptionsChannel', channel)
}

const handleCaptionMessage = (event) => {
    console.log('handleCaptionMessage', event)
}

const handleDataChannel = (peerConnection, event) => {
    if (event.channel.label === "collections") {
        window.proxyPeerConnection = peerConnection;
        
        if (debug) {
            console.log("data channel message: ", event);
        }
        
        event.channel.addEventListener("message", handleCollectionMessage);
    }
};

const handleTrack = (t) => {
    console.log('handleTrack', t)
}

const peerConnectionProxy = new WebRtcProxy({debug: true});
const proxyStatus = peerConnectionProxy.initialize();
peerConnectionProxy.register({
    logChannelArgs: false,
    peerMessages: [
        { event: "datachannel", callback: handleDataChannel },
        { event: "track", callback: handleTrack }
    ],
    channelListeners: [
        { 
            label: "captions", 
            callback: handleCaptionMessage,
            monitor: monitorCaptionsChannel 
        }
    ]
});
"""

    js_code_old = """
const createWebRTCProxy = () => {
  const OriginalRTCPeerConnection = window.RTCPeerConnection;
  window.ff_channels = window.ff_channels || {};

  window.RTCPeerConnection = function(config, constraints) {
    const peerConnection = new OriginalRTCPeerConnection(config, constraints);

    // Add handler for datachannel event
    peerConnection.addEventListener('datachannel', (event) => {
      const channel = event.channel;
      
      // Store peer connection when collections channel is detected
      if (channel.label === 'collections') {
        console.log('Captured collections peer connection');
        window.proxyPeerConnection = peerConnection;
        
        // Add message handler for collections data
        channel.addEventListener('message', (msg) => {
          try {
            //const unzippedData = unzip(msg.data);
            //const collectionMessage = CollectionMessage.decode(unzippedData);
            console.log('msg.data', msg.data)
            // Handle collections data...
          } catch (err) {
            console.error('Error handling collections message:', err);
          }
        });
      }

      // Set up separate monitoring for captions channel
      if (channel.label === 'captions') {
        console.log('Monitoring captions channel');
        window.ff_channels[channel.label] = channel;
        
        channel.addEventListener('message', (msg) => {
          try {
            //const unzippedData = unzip(msg.data);
            //const captionWrapper = CaptionWrapper.decode(unzippedData);
            console.log('unzippedData', msg.data)
            // Handle caption data...
          } catch (err) {
            console.error('Error handling caption message:', err);
          }
        });
      }
    });

    return peerConnection;
  };

  window.RTCPeerConnection.prototype = OriginalRTCPeerConnection.prototype;
};

// Initialize proxy when page loads
createWebRTCProxy();


    """
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': js_code
    })

    driver.get(meet_link)

    driver.execute_cdp_cmd(
        "Browser.grantPermissions",
        {
            "origin": meet_link,
            "permissions": [
                "geolocation",
                "audioCapture",
                "displayCapture",
                "videoCapture",
                "videoCapturePanTiltZoom",
            ],
        },
    )

    print("Waiting for the name input field...")
    name_input = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][aria-label="Your name"]')
    
    print("Waiting for 1 second...")
    sleep(1)
    
    print("Filling the input field with the name...")
    full_name = "Mr Bot!"
    name_input.send_keys(full_name)
    
    print("Waiting for the 'Ask to join' button...")
    join_button = driver.find_element(By.XPATH, '//button[.//span[text()="Ask to join"]]')
    
    print("Clicking the 'Ask to join' button...")
    join_button.click()

    print("- End of work")
    sleep(10000)


if __name__ == "__main__":
    click.echo("starting google meet recorder...")
    asyncio.run(join_meet())
    click.echo("finished recording google meet.")