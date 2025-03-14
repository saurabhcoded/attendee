// Video track manager
class VideoTrackManager {
    constructor(ws) {
        this.videoTracks = new Map();
        this.ws = ws;
        this.trackToSendCache = null;
    }

    deleteVideoTrack(videoTrack) {
        this.videoTracks.delete(videoTrack.id);
        this.trackToSendCache = null;
    }

    upsertVideoTrack(videoTrack, streamId, isScreenShare) {
        const existingVideoTrack = this.videoTracks.get(videoTrack.id);

        // Create new object with track info and firstSeenAt timestamp
        const trackInfo = {
            originalTrack: videoTrack,
            isScreenShare: isScreenShare,
            firstSeenAt: existingVideoTrack ? existingVideoTrack.firstSeenAt : Date.now(),
            streamId: streamId
        };
 
        console.log('upsertVideoTrack for', videoTrack.id, '=', trackInfo);
        
        this.videoTracks.set(videoTrack.id, trackInfo);
        this.trackToSendCache = null;
    }

    getStreamIdToSendCached() {
        return this.getTrackToSendCached()?.streamId;
    }

    getTrackToSendCached() {
        if (this.trackToSendCache) {
            return this.trackToSendCache;
        }

        this.trackToSendCache = this.getTrackToSend();
        return this.trackToSendCache;
    }

    getTrackToSend() {
        const screenShareTracks = Array.from(this.videoTracks.values()).filter(track => track.isScreenShare);
        const mostRecentlyCreatedScreenShareTrack = screenShareTracks.reduce((max, track) => {
            return track.firstSeenAt > max.firstSeenAt ? track : max;
        }, screenShareTracks[0]);

        if (mostRecentlyCreatedScreenShareTrack) {
            return mostRecentlyCreatedScreenShareTrack;
        }

        const nonScreenShareTracks = Array.from(this.videoTracks.values()).filter(track => !track.isScreenShare);
        const mostRecentlyCreatedNonScreenShareTrack = nonScreenShareTracks.reduce((max, track) => {
            return track.firstSeenAt > max.firstSeenAt ? track : max;
        }, nonScreenShareTracks[0]);

        if (mostRecentlyCreatedNonScreenShareTrack) {
            return mostRecentlyCreatedNonScreenShareTrack;
        }

        return null;
    }
}

// Caption manager
class CaptionManager {
    constructor(ws) {
        this.captions = new Map();
        this.ws = ws;
    }

    singleCaptionSynced(caption) {
        this.captions.set(caption.captionId, caption);
        this.ws.sendClosedCaptionUpdate(caption);
    }
}

const DEVICE_OUTPUT_TYPE = {
    AUDIO: 1,
    VIDEO: 2
}

// User manager
class UserManager {
    constructor(ws) {
        this.allUsersMap = new Map();
        this.currentUsersMap = new Map();
        this.deviceOutputMap = new Map();

        this.ws = ws;
    }

    deviceForStreamIsActive(streamId) {
        for(const deviceOutput of this.deviceOutputMap.values()) {
            if (deviceOutput.streamId === streamId) {
                return !deviceOutput.disabled;
            }
        }

        return false;
    }

    getDeviceOutput(deviceId, outputType) {
        return this.deviceOutputMap.get(`${deviceId}-${outputType}`);
    }

    updateDeviceOutputs(deviceOutputs) {
        for (const output of deviceOutputs) {
            const key = `${output.deviceId}-${output.deviceOutputType}`; // Unique key combining device ID and output type

            const deviceOutput = {
                deviceId: output.deviceId,
                outputType: output.deviceOutputType, // 1 = audio, 2 = video
                streamId: output.streamId,
                disabled: output.deviceOutputStatus.disabled,
                lastUpdated: Date.now()
            };

            this.deviceOutputMap.set(key, deviceOutput);
        }

        // Notify websocket clients about the device output update
        this.ws.sendJson({
            type: 'DeviceOutputsUpdate',
            deviceOutputs: Array.from(this.deviceOutputMap.values())
        });
    }

    getUserByDeviceId(deviceId) {
        return this.allUsersMap.get(deviceId);
    }

    // constants for meeting status
    MEETING_STATUS = {
        IN_MEETING: 1,
        NOT_IN_MEETING: 6
    }

    getCurrentUsersInMeeting() {
        return Array.from(this.currentUsersMap.values()).filter(user => user.status === this.MEETING_STATUS.IN_MEETING);
    }

    getCurrentUsersInMeetingWhoAreScreenSharing() {
        return this.getCurrentUsersInMeeting().filter(user => user.parentDeviceId);
    }

    singleUserSynced(user) {
      // Create array with new user and existing users, then filter for unique deviceIds
      // keeping the first occurrence (new user takes precedence)
      const allUsers = [...this.currentUsersMap.values(), user];
      const uniqueUsers = Array.from(
        new Map(allUsers.map(user => [user.deviceId, user])).values()
      );
      this.newUsersListSynced(uniqueUsers);
    }

    newUsersListSynced(newUsersListRaw) {
        const newUsersList = newUsersListRaw.map(user => {
            const userStatusMap = {
                1: 'in_meeting',
                6: 'not_in_meeting',
                7: 'removed_from_meeting'
            }

            return {
                ...user,
                humanized_status: userStatusMap[user.status] || "unknown"
            }
        })
        // Get the current user IDs before updating
        const previousUserIds = new Set(this.currentUsersMap.keys());
        const newUserIds = new Set(newUsersList.map(user => user.deviceId));
        const updatedUserIds = new Set([])

        // Update all users map
        for (const user of newUsersList) {
            if (previousUserIds.has(user.deviceId) && JSON.stringify(this.currentUsersMap.get(user.deviceId)) !== JSON.stringify(user)) {
                updatedUserIds.add(user.deviceId);
            }

            this.allUsersMap.set(user.deviceId, {
                deviceId: user.deviceId,
                displayName: user.displayName,
                fullName: user.fullName,
                profile: user.profile,
                status: user.status,
                humanized_status: user.humanized_status,
                parentDeviceId: user.parentDeviceId
            });
        }

        // Calculate new, removed, and updated users
        const newUsers = newUsersList.filter(user => !previousUserIds.has(user.deviceId));
        const removedUsers = Array.from(previousUserIds)
            .filter(id => !newUserIds.has(id))
            .map(id => this.currentUsersMap.get(id));

        // Clear current users map and update with new list
        this.currentUsersMap.clear();
        for (const user of newUsersList) {
            this.currentUsersMap.set(user.deviceId, {
                deviceId: user.deviceId,
                displayName: user.displayName,
                fullName: user.fullName,
                profilePicture: user.profilePicture,
                status: user.status,
                humanized_status: user.humanized_status,
                parentDeviceId: user.parentDeviceId
            });
        }

        const updatedUsers = Array.from(updatedUserIds).map(id => this.currentUsersMap.get(id));

        if (newUsers.length > 0 || removedUsers.length > 0 || updatedUsers.length > 0) {
            this.ws.sendJson({
                type: 'UsersUpdate',
                newUsers: newUsers,
                removedUsers: removedUsers,
                updatedUsers: updatedUsers
            });
        }
    }
}

// Websocket client
class WebSocketClient {
  // Message types
  static MESSAGE_TYPES = {
      JSON: 1,
      VIDEO: 2,  // Reserved for future use
      AUDIO: 3   // Reserved for future use
  };

  constructor() {
      const url = `ws://localhost:${window.initialData.websocketPort}`;
      console.log('WebSocketClient url', url);
      this.ws = new WebSocket(url);
      this.ws.binaryType = 'arraybuffer';
      
      this.ws.onopen = () => {
          console.log('WebSocket Connected');
      };
      
      this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
      };
      
      this.ws.onerror = (error) => {
          console.error('WebSocket Error:', error);
      };
      
      this.ws.onclose = () => {
          console.log('WebSocket Disconnected');
      };

      this.mediaSendingEnabled = false;
      this.lastVideoFrameTime = performance.now();
      this.fillerFrameInterval = null;

      this.lastVideoFrame = this.getBlackFrame();
      this.blackVideoFrame = this.getBlackFrame();
  }

  getBlackFrame() {
    // Create black frame data (I420 format)
    const width = 1920, height = 1080;
    const yPlaneSize = width * height;
    const uvPlaneSize = (width * height) / 4;

    const frameData = new Uint8Array(yPlaneSize + 2 * uvPlaneSize);
    // Y plane (black = 0)
    frameData.fill(0, 0, yPlaneSize);
    // U and V planes (black = 128)
    frameData.fill(128, yPlaneSize);

    return {width, height, frameData};
  }

  currentVideoStreamIsActive() {
    const result = window.userManager?.deviceForStreamIsActive(window.videoTrackManager?.getStreamIdToSendCached());

    // This avoids a situation where we transition from no video stream to video stream and we send a filler frame from the
    // last time we had a video stream and it's not the same as the current video stream.
    if (!result)
        this.lastVideoFrame = this.blackVideoFrame;

    return result;
  }

  startFillerFrameTimer() {
    if (this.fillerFrameInterval) return; // Don't start if already running
    
    this.fillerFrameInterval = setInterval(() => {
        try {
            const currentTime = performance.now();
            if (currentTime - this.lastVideoFrameTime >= 500 && this.mediaSendingEnabled) {                
                // Fix: Math.floor() the milliseconds before converting to BigInt
                const currentTimeMicros = BigInt(Math.floor(currentTime) * 1000);
                const frameToUse = this.currentVideoStreamIsActive() ? this.lastVideoFrame : this.blackVideoFrame;
                this.sendVideo(currentTimeMicros, '0', frameToUse.width, frameToUse.height, frameToUse.frameData);
            }
        } catch (error) {
            console.error('Error in black frame timer:', error);
        }
    }, 250);
  }

    stopFillerFrameTimer() {
        if (this.fillerFrameInterval) {
            clearInterval(this.fillerFrameInterval);
            this.fillerFrameInterval = null;
        }
    }

  enableMediaSending() {
    this.mediaSendingEnabled = true;
    this.startFillerFrameTimer();
  }

  disableMediaSending() {
    this.mediaSendingEnabled = false;
    this.stopFillerFrameTimer();
  }

  handleMessage(data) {
      const view = new DataView(data);
      const messageType = view.getInt32(0, true); // true for little-endian
      
      // Handle different message types
      switch (messageType) {
          case WebSocketClient.MESSAGE_TYPES.JSON:
              const jsonData = new TextDecoder().decode(new Uint8Array(data, 4));
              console.log('Received JSON message:', JSON.parse(jsonData));
              break;
          // Add future message type handlers here
          default:
              console.warn('Unknown message type:', messageType);
      }
  }
  
  sendJson(data) {
      if (this.ws.readyState !== WebSocket.OPEN) {
          console.error('WebSocket is not connected');
          return;
      }

      try {
          // Convert JSON to string then to Uint8Array
          const jsonString = JSON.stringify(data);
          const jsonBytes = new TextEncoder().encode(jsonString);
          
          // Create final message: type (4 bytes) + json data
          const message = new Uint8Array(4 + jsonBytes.length);
          
          // Set message type (1 for JSON)
          new DataView(message.buffer).setInt32(0, WebSocketClient.MESSAGE_TYPES.JSON, true);
          
          // Copy JSON data after type
          message.set(jsonBytes, 4);
          
          // Send the binary message
          this.ws.send(message.buffer);
      } catch (error) {
          console.error('Error sending WebSocket message:', error);
          console.error('Message data:', data);
      }
  }

  sendClosedCaptionUpdate(item) {
    if (!this.mediaSendingEnabled)
        return;

    this.sendJson({
        type: 'CaptionUpdate',
        caption: item
    });
  }

  sendAudio(timestamp, streamId, audioData) {
      if (this.ws.readyState !== WebSocket.OPEN) {
          console.error('WebSocket is not connected for audio send', this.ws.readyState);
          return;
      }


      if (!this.mediaSendingEnabled) {
        return;
      }

      try {
          // Create final message: type (4 bytes) + timestamp (8 bytes) + audio data
          const message = new Uint8Array(4 + 8 + 4 + audioData.buffer.byteLength);
          const dataView = new DataView(message.buffer);
          
          // Set message type (3 for AUDIO)
          dataView.setInt32(0, WebSocketClient.MESSAGE_TYPES.AUDIO, true);
          
          // Set timestamp as BigInt64
          dataView.setBigInt64(4, BigInt(timestamp), true);

          // Set streamId length and bytes
          dataView.setInt32(12, streamId, true);

          // Copy audio data after type and timestamp
          message.set(new Uint8Array(audioData.buffer), 16);
          
          // Send the binary message
          this.ws.send(message.buffer);
      } catch (error) {
          console.error('Error sending WebSocket audio message:', error);
      }
  }

  sendVideo(timestamp, streamId, width, height, videoData) {
      if (this.ws.readyState !== WebSocket.OPEN) {
          console.error('WebSocket is not connected for video send', this.ws.readyState);
          return;
      }

      if (!this.mediaSendingEnabled) {
        return;
      }
      
      this.lastVideoFrameTime = performance.now();
      this.lastVideoFrame = {width, height, frameData: videoData};
      
      try {
          // Convert streamId to UTF-8 bytes
          const streamIdBytes = new TextEncoder().encode(streamId);
          
          // Create final message: type (4 bytes) + timestamp (8 bytes) + streamId length (4 bytes) + 
          // streamId bytes + width (4 bytes) + height (4 bytes) + video data
          const message = new Uint8Array(4 + 8 + 4 + streamIdBytes.length + 4 + 4 + videoData.buffer.byteLength);
          const dataView = new DataView(message.buffer);
          
          // Set message type (2 for VIDEO)
          dataView.setInt32(0, WebSocketClient.MESSAGE_TYPES.VIDEO, true);
          
          // Set timestamp as BigInt64
          dataView.setBigInt64(4, BigInt(timestamp), true);

          // Set streamId length and bytes
          dataView.setInt32(12, streamIdBytes.length, true);
          message.set(streamIdBytes, 16);

          // Set width and height
          const streamIdOffset = 16 + streamIdBytes.length;
          dataView.setInt32(streamIdOffset, width, true);
          dataView.setInt32(streamIdOffset + 4, height, true);

          // Copy video data after headers
          message.set(new Uint8Array(videoData.buffer), streamIdOffset + 8);
          
          // Send the binary message
          this.ws.send(message.buffer);
      } catch (error) {
          console.error('Error sending WebSocket video message:', error);
      }
  }
}

// Interceptors

class FetchInterceptor {
    constructor(responseCallback) {
        this.originalFetch = window.fetch;
        this.responseCallback = responseCallback;
        window.fetch = (...args) => this.interceptFetch(...args);
    }

    async interceptFetch(...args) {
        try {
            // Call the original fetch
            const response = await this.originalFetch.apply(window, args);
            
            // Clone the response since it can only be consumed once
            const clonedResponse = response.clone();
            
            // Call the callback with the cloned response
            await this.responseCallback(clonedResponse);
            
            // Return the original response to maintain normal flow
            return response;
        } catch (error) {
            console.error('Error in intercepted fetch:', error);
            throw error;
        }
    }
}
class RTCInterceptor {
    constructor(callbacks) {
        // Store the original RTCPeerConnection
        const originalRTCPeerConnection = window.RTCPeerConnection;
        
        // Store callbacks
        const onPeerConnectionCreate = callbacks.onPeerConnectionCreate || (() => {});
        const onDataChannelCreate = callbacks.onDataChannelCreate || (() => {});
        
        // Override the RTCPeerConnection constructor
        window.RTCPeerConnection = function(...args) {
            // Create instance using the original constructor
            const peerConnection = Reflect.construct(
                originalRTCPeerConnection, 
                args
            );
            
            // Notify about the creation
            onPeerConnectionCreate(peerConnection);
            
            // Override createDataChannel
            const originalCreateDataChannel = peerConnection.createDataChannel.bind(peerConnection);
            peerConnection.createDataChannel = (label, options) => {
                const dataChannel = originalCreateDataChannel(label, options);
                onDataChannelCreate(dataChannel, peerConnection);
                return dataChannel;
            };
            
            return peerConnection;
        };
    }
}

// Message type definitions
const messageTypes = [
      {
        name: 'CollectionEvent',
        fields: [
            { name: 'body', fieldNumber: 1, type: 'message', messageType: 'CollectionEventBody' }
        ]
    },
    {
        name: 'CollectionEventBody',
        fields: [
            { name: 'userInfoListWrapperAndChatWrapperWrapper', fieldNumber: 2, type: 'message', messageType: 'UserInfoListWrapperAndChatWrapperWrapper' }
        ]
    },
    {
        name: 'UserInfoListWrapperAndChatWrapperWrapper',
        fields: [
            { name: 'deviceInfoWrapper', fieldNumber: 3, type: 'message', messageType: 'DeviceInfoWrapper' },
            { name: 'userInfoListWrapperAndChatWrapper', fieldNumber: 13, type: 'message', messageType: 'UserInfoListWrapperAndChatWrapper' }
        ]
    },
    {
        name: 'UserInfoListWrapperAndChatWrapper',
        fields: [
            { name: 'userInfoListWrapper', fieldNumber: 1, type: 'message', messageType: 'UserInfoListWrapper' },
            { name: 'chatMessageWrapper', fieldNumber: 4, type: 'message', messageType: 'ChatMessageWrapper', repeated: true }
        ]
    },
    {
        name: 'DeviceInfoWrapper',
        fields: [
            { name: 'deviceOutputInfoList', fieldNumber: 2, type: 'message', messageType: 'DeviceOutputInfoList', repeated: true }
        ]
    },
    {
        name: 'DeviceOutputInfoList',
        fields: [
            { name: 'deviceOutputType', fieldNumber: 2, type: 'varint' }, // Speculating that 1 = audio, 2 = video
            { name: 'streamId', fieldNumber: 4, type: 'string' },
            { name: 'deviceId', fieldNumber: 6, type: 'string' },
            { name: 'deviceOutputStatus', fieldNumber: 10, type: 'message', messageType: 'DeviceOutputStatus' }
        ]
    },
    {
        name: 'DeviceOutputStatus',
        fields: [
            { name: 'disabled', fieldNumber: 1, type: 'varint' }
        ]
    },
    // Existing message types
    {
        name: 'UserInfoListResponse',
        fields: [
            { name: 'userInfoListWrapperWrapper', fieldNumber: 2, type: 'message', messageType: 'UserInfoListWrapperWrapper' }
        ]
    },
    {
        name: 'UserInfoListResponse',
        fields: [
            { name: 'userInfoListWrapperWrapper', fieldNumber: 2, type: 'message', messageType: 'UserInfoListWrapperWrapper' }
        ]
    },
    {
        name: 'UserInfoListWrapperWrapper',
        fields: [
            { name: 'userInfoListWrapper', fieldNumber: 2, type: 'message', messageType: 'UserInfoListWrapper' }
        ]
    },
    {
        name: 'UserEventInfo',
        fields: [
            { name: 'eventNumber', fieldNumber: 1, type: 'varint' } // sequence number for the event
        ]
    },
    {
        name: 'UserInfoListWrapper',
        fields: [
            { name: 'userEventInfo', fieldNumber: 1, type: 'message', messageType: 'UserEventInfo' },
            { name: 'userInfoList', fieldNumber: 2, type: 'message', messageType: 'UserInfoList', repeated: true }
        ]
    },
    {
        name: 'UserInfoList',
        fields: [
            { name: 'deviceId', fieldNumber: 1, type: 'string' },
            { name: 'fullName', fieldNumber: 2, type: 'string' },
            { name: 'profilePicture', fieldNumber: 3, type: 'string' },
            { name: 'status', fieldNumber: 4, type: 'varint' }, // in meeting = 1 vs not in meeting = 6. kicked out = 7?
            { name: 'displayName', fieldNumber: 29, type: 'string' },
            { name: 'parentDeviceId', fieldNumber: 21, type: 'string' } // if this is present, then this is a screenshare device. The parentDevice is the person that is sharing
        ]
    },
    {
        name: 'CaptionWrapper',
        fields: [
            { name: 'caption', fieldNumber: 1, type: 'message', messageType: 'Caption' }
        ]
    },
    {
        name: 'Caption',
        fields: [
            { name: 'deviceId', fieldNumber: 1, type: 'string' },
            { name: 'captionId', fieldNumber: 2, type: 'int64' },
            { name: 'version', fieldNumber: 3, type: 'int64' },
            { name: 'text', fieldNumber: 6, type: 'string' },
            { name: 'languageId', fieldNumber: 8, type: 'int64' }
        ]
    },
    {
        name: 'ChatMessageWrapper',
        fields: [
            { name: 'chatMessage', fieldNumber: 2, type: 'message', messageType: 'ChatMessage' }
        ]
    },
    {
        name: 'ChatMessage',
        fields: [
            { name: 'messageId', fieldNumber: 1, type: 'string' },
            { name: 'deviceId', fieldNumber: 2, type: 'string' },
            { name: 'timestamp', fieldNumber: 3, type: 'int64' },
            { name: 'chatMessageContent', fieldNumber: 5, type: 'message', messageType: 'ChatMessageContent' }
        ]
    },
    {
        name: 'ChatMessageContent',
        fields: [
            { name: 'text', fieldNumber: 1, type: 'string' }
        ]
    }
];

// Generic message decoder factory
function createMessageDecoder(messageType) {
    return function decode(reader, length) {
        if (!(reader instanceof protobuf.Reader)) {
            reader = protobuf.Reader.create(reader);
        }

        const end = length === undefined ? reader.len : reader.pos + length;
        const message = {};

        while (reader.pos < end) {
            const tag = reader.uint32();
            const fieldNumber = tag >>> 3;
            
            const field = messageType.fields.find(f => f.fieldNumber === fieldNumber);
            if (!field) {
                reader.skipType(tag & 7);
                continue;
            }

            let value;
            switch (field.type) {
                case 'string':
                    value = reader.string();
                    break;
                case 'int64':
                    value = reader.int64();
                    break;
                case 'varint':
                    value = reader.uint32();
                    break;
                case 'message':
                    value = messageDecoders[field.messageType](reader, reader.uint32());
                    break;
                default:
                    reader.skipType(tag & 7);
                    continue;
            }

            if (field.repeated) {
                if (!message[field.name]) {
                    message[field.name] = [];
                }
                message[field.name].push(value);
            } else {
                message[field.name] = value;
            }
        }

        return message;
    };
}

const ws = new WebSocketClient();
window.ws = ws;
const userManager = new UserManager(ws);
const captionManager = new CaptionManager(ws);
const videoTrackManager = new VideoTrackManager(ws);
window.videoTrackManager = videoTrackManager;
window.userManager = userManager;

// Create decoders for all message types
const messageDecoders = {};
messageTypes.forEach(type => {
    messageDecoders[type.name] = createMessageDecoder(type);
});

function base64ToUint8Array(base64) {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
}

const syncMeetingSpaceCollectionsUrl = "https://meet.google.com/$rpc/google.rtc.meetings.v1.MeetingSpaceService/SyncMeetingSpaceCollections";
const userMap = new Map();
new FetchInterceptor(async (response) => {
    if (response.url === syncMeetingSpaceCollectionsUrl) {
        const responseText = await response.text();
        const decodedData = base64ToUint8Array(responseText);
        const userInfoListResponse = messageDecoders['UserInfoListResponse'](decodedData);
        const userInfoList = userInfoListResponse.userInfoListWrapperWrapper?.userInfoListWrapper?.userInfoList || [];
        console.log('userInfoList', userInfoList);
        if (userInfoList.length > 0) {
            userManager.newUsersListSynced(userInfoList);
        }
    }
});

const handleCollectionEvent = (event) => {
  const decodedData = pako.inflate(new Uint8Array(event.data));
  //console.log(' handleCollectionEventdecodedData', decodedData);
  // Convert decoded data to base64
  const base64Data = btoa(String.fromCharCode.apply(null, decodedData));
  //console.log('Decoded collection event data (base64):', base64Data);

  const collectionEvent = messageDecoders['CollectionEvent'](decodedData);
  
  const deviceOutputInfoList = collectionEvent.body.userInfoListWrapperAndChatWrapperWrapper?.deviceInfoWrapper?.deviceOutputInfoList;
  if (deviceOutputInfoList) {
    userManager.updateDeviceOutputs(deviceOutputInfoList);
  }

  const chatMessageWrapper = collectionEvent.body.userInfoListWrapperAndChatWrapperWrapper?.userInfoListWrapperAndChatWrapper?.chatMessageWrapper;
  if (chatMessageWrapper) {
    console.log('chatMessageWrapper', chatMessageWrapper);
  }

  //console.log('deviceOutputInfoList', JSON.stringify(collectionEvent.body.userInfoListWrapperAndChatWrapperWrapper?.deviceInfoWrapper?.deviceOutputInfoList));
  //console.log('usermap', userMap.allUsersMap);
  //console.log('userInfoList And Event', collectionEvent.body.userInfoListWrapperAndChatWrapperWrapper.userInfoListWrapperAndChatWrapper.userInfoListWrapper);
  const userInfoList = collectionEvent.body.userInfoListWrapperAndChatWrapperWrapper.userInfoListWrapperAndChatWrapper.userInfoListWrapper?.userInfoList || [];
  console.log('userInfoList in collection event', userInfoList);
  // This event is triggered when a single user joins (or leaves) the meeting
  // generally this array only contains a single user
  // we can't tell whether the event is a join or leave event, so we'll assume it's a join
  // if it's a leave, then we'll pick it up from the periodic call to syncMeetingSpaceCollections
  // so there will be a lag of roughly a minute for leave events
  for (const user of userInfoList) {
    userManager.singleUserSynced(user);
  }
};

// the stream ID, not the track id in the TRACK appears in the payload of the protobuf message somewhere

const handleCaptionEvent = (event) => {
  const decodedData = new Uint8Array(event.data);
  const captionWrapper = messageDecoders['CaptionWrapper'](decodedData);
  const caption = captionWrapper.caption;
  captionManager.singleCaptionSynced(caption);
}

const handleMediaDirectorEvent = (event) => {
  console.log('handleMediaDirectorEvent', event);
  const decodedData = new Uint8Array(event.data);
  //console.log(' handleCollectionEventdecodedData', decodedData);
  // Convert decoded data to base64
  const base64Data = btoa(String.fromCharCode.apply(null, decodedData));
  console.log('Decoded media director event data (base64):', base64Data);
}

const addTrackToDOM = (event) => {
        // Create a new MediaStream with the video track and first audio track
        const previewStream = new MediaStream();
        previewStream.addTrack(event.track);
        
        // Add the first audio track if available
        if (globalAudioTracks.length > 0) {
          previewStream.addTrack(globalAudioTracks[0]);
        }
        
        // Create a container div to hold video and controls
        const videoContainer = document.createElement('div');
        videoContainer.style.position = 'fixed';
        videoContainer.style.bottom = '10px';
        videoContainer.style.right = '10px';
        videoContainer.style.zIndex = '9999';
        
        // Create a video element for preview
        const videoElement = document.createElement('video');
        videoElement.srcObject = previewStream;
        videoElement.autoplay = true;
        videoElement.muted = false; // Not muted so we can hear audio
        videoElement.style.width = '240px';
        videoElement.style.height = '180px';
        videoElement.style.border = '2px solid #00a2ff';
        videoElement.style.borderRadius = '4px';
        
        // Create recording controls
        const controlsDiv = document.createElement('div');
        controlsDiv.style.display = 'flex';
        controlsDiv.style.justifyContent = 'space-between';
        controlsDiv.style.marginTop = '5px';
        
        // Create record button
        const recordButton = document.createElement('button');
        recordButton.textContent = '⚫ Record';
        recordButton.style.backgroundColor = '#00a2ff';
        recordButton.style.color = 'white';
        recordButton.style.border = 'none';
        recordButton.style.borderRadius = '4px';
        recordButton.style.padding = '5px 10px';
        recordButton.style.cursor = 'pointer';
        
        // Create download link (initially hidden)
        const downloadLink = document.createElement('a');
        downloadLink.textContent = '💾 Download';
        downloadLink.style.backgroundColor = '#4CAF50';
        downloadLink.style.color = 'white';
        downloadLink.style.textDecoration = 'none';
        downloadLink.style.borderRadius = '4px';
        downloadLink.style.padding = '5px 10px';
        downloadLink.style.display = 'none';
        
        // Add status text
        const statusText = document.createElement('div');
        statusText.style.marginTop = '5px';
        statusText.style.fontSize = '12px';
        statusText.style.color = '#333';
        
        // Add elements to container
        controlsDiv.appendChild(recordButton);
        controlsDiv.appendChild(downloadLink);
        videoContainer.appendChild(videoElement);
        videoContainer.appendChild(controlsDiv);
        videoContainer.appendChild(statusText);
        
        // Add the container to the document
        document.body.appendChild(videoContainer);
        
        // Set up MediaRecorder and recording logic
        let mediaRecorder;
        let recordedChunks = [];
        let isRecording = false;
        let recordingStartTime;
        let recordingTimer;
        
        // Find supported MIME type
        const getMimeType = () => {
          const types = [
            'video/mp4;codecs=h264,aac',
          ];
          
          for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
              console.log('Using MIME type:', type);
              return type;
            }
          }
          return 'video/mp4'; // Default fallback
        };
        
        // Initialize MediaRecorder
        try {
          // Play the video first to ensure media is flowing
          const playPromise = videoElement.play();
          if (playPromise !== undefined) {
            playPromise.then(() => {
              console.log('Video is playing, stream should be active');
              statusText.textContent = 'Stream ready for recording';
            }).catch(err => {
              console.error('Failed to play video:', err);
              statusText.textContent = 'Error: Could not play video stream';
            });
          }
          
          mediaRecorder = new MediaRecorder(videoElement.captureStream(), { 
            mimeType: getMimeType()          });
          
          console.log('MediaRecorder state:', mediaRecorder.state);
          console.log('MediaRecorder options:', mediaRecorder.mimeType);
          
          mediaRecorder.ondataavailable = (e) => {
            console.log('Data available event, size:', e.data.size);
            if (e.data && e.data.size > 0) {
              recordedChunks.push(e.data);
              statusText.textContent = `Recording: ${recordedChunks.length} chunks captured (${Math.round(e.data.size / 1024)} KB)`;
            }
          };
          
          mediaRecorder.onstart = () => {
            console.log('MediaRecorder started');
            recordingStartTime = Date.now();
            statusText.textContent = 'Recording started...';
            
            // Update recording time display
            recordingTimer = setInterval(() => {
              const duration = Math.floor((Date.now() - recordingStartTime) / 1000);
              const minutes = Math.floor(duration / 60).toString().padStart(2, '0');
              const seconds = (duration % 60).toString().padStart(2, '0');
              statusText.textContent = `Recording: ${minutes}:${seconds}`;
            }, 1000);
          };
          
          mediaRecorder.onstop = () => {
            console.log('MediaRecorder stopped, chunks:', recordedChunks.length);
            clearInterval(recordingTimer);
            
            if (recordedChunks.length === 0) {
              statusText.textContent = 'Error: No data was recorded';
              return;
            }
            
            // Create blob from recorded chunks
            const blob = new Blob(recordedChunks, { type: mediaRecorder.mimeType });
            console.log('Created blob, size:', blob.size);
            statusText.textContent = `Recording complete: ${Math.round(blob.size / 1024 / 1024 * 100) / 100} MB`;
            
            const url = URL.createObjectURL(blob);
            
            // Update download link
            downloadLink.href = url;
            downloadLink.download = `screen-recording-${new Date().toISOString().replace(/:/g, '-')}.mp4`;
            downloadLink.style.display = 'block';
            
            // Reset recording state
            isRecording = false;
            recordButton.textContent = '⚫ Record';
            recordButton.style.backgroundColor = '#00a2ff';
          };
          
          mediaRecorder.onerror = (event) => {
            console.error('MediaRecorder error:', event);
            statusText.textContent = 'Error during recording';
          };
          
          // Add click event to record button
          recordButton.addEventListener('click', () => {
            if (isRecording) {
              // Stop recording
              mediaRecorder.stop();
              recordButton.textContent = '⚫ Record';
              recordButton.style.backgroundColor = '#00a2ff';
            } else {
              // Start recording
              recordedChunks = [];
              try {
                mediaRecorder.start(1000); // Request data every second
                isRecording = true;
                recordButton.textContent = '⏹️ Stop';
                recordButton.style.backgroundColor = '#ff4d4d';
                downloadLink.style.display = 'none';
              } catch (err) {
                console.error('Failed to start recording:', err);
                statusText.textContent = `Error starting recording: ${err.message}`;
              }
            }
          });
          
        } catch (error) {
          console.error('MediaRecorder initialization error:', error);
          statusText.textContent = `Recording not supported: ${error.message}`;
          recordButton.textContent = 'Recording not supported';
          recordButton.disabled = true;
          recordButton.style.backgroundColor = '#cccccc';
        }
}

const handleVideoTrack = async (event) => {  
  try {

    // Create processor to get raw frames
    const processor = new MediaStreamTrackProcessor({ track: event.track });
    const generator = new MediaStreamTrackGenerator({ kind: 'video' });
    
    // Add track ended listener
    event.track.addEventListener('ended', () => {
        console.log('Video track ended:', event.track.id);
        videoTrackManager.deleteVideoTrack(event.track);
    });
    
    // Get readable stream of video frames
    const readable = processor.readable;
    const writable = generator.writable;

    const firstStreamId = event.streams[0]?.id;

    // Check if of the users who are in the meeting and screensharers
    // if any of them have an associated device output with the first stream ID of this video track
    const isScreenShare = userManager
        .getCurrentUsersInMeetingWhoAreScreenSharing()
        .some(user => firstStreamId && userManager.getDeviceOutput(user.deviceId, DEVICE_OUTPUT_TYPE.VIDEO).streamId === firstStreamId);
    if (firstStreamId) {
        videoTrackManager.upsertVideoTrack(event.track, firstStreamId, isScreenShare);
    }

    // Add frame rate control variables
    const targetFPS = 1000;//isScreenShare ? 5 : 15;
    const frameInterval = 1000 / targetFPS; // milliseconds between frames
    let lastFrameTime = 0;
    let firstFrame = null;

    const transformStream = new TransformStream({
        async transform(frame, controller) {
            if (!frame) {
                return;
            }

            try {
                // Check if controller is still active
                if (controller.desiredSize === null) {
                    frame.close();
                    return;
                }

                const currentTime = performance.now();
                
                if (firstStreamId && firstStreamId === videoTrackManager.getStreamIdToSendCached()) {
                    // Check if enough time has passed since the last frame
                    if (currentTime - lastFrameTime >= frameInterval) {
                        // Copy the frame to get access to raw data
                        const rawFrame = new VideoFrame(frame, {
                            format: 'I420'
                        });

                        // Get the raw data from the frame
                        const data = new Uint8Array(rawFrame.allocationSize());
                        rawFrame.copyTo(data);

                        /*
                        const currentFormat = {
                            width: frame.displayWidth,
                            height: frame.displayHeight,
                            dataSize: data.length,
                            format: rawFrame.format,
                            duration: frame.duration,
                            colorSpace: frame.colorSpace,
                            codedWidth: frame.codedWidth,
                            codedHeight: frame.codedHeight
                        };
                        */
                        // Get current time in microseconds (multiply milliseconds by 1000)
                        const currentTimeMicros = BigInt(Math.floor(currentTime * 1000));
                        ws.sendVideo(currentTimeMicros, firstStreamId, frame.displayWidth, frame.displayHeight, data);

                        rawFrame.close();
                        lastFrameTime = currentTime;
                        if (firstFrame === null) {
                            firstFrame = "Dfdf";

                            addTrackToDOM(event);
                        }
                    }
                }
                
                // Always enqueue the frame for the video element
                controller.enqueue(frame);
            } catch (error) {
                console.error('Error processing frame:', error);
                frame.close();
            }
        },
        flush() {
            console.log('Transform stream flush called');
        }
    });

    // Create an abort controller for cleanup
    const abortController = new AbortController();

    try {
        // Connect the streams
        await readable
            .pipeThrough(transformStream)
            .pipeTo(writable, {
                signal: abortController.signal
            })
            .catch(error => {
                if (error.name !== 'AbortError') {
                    console.error('Pipeline error:', error);
                }
            });
    } catch (error) {
        console.error('Stream pipeline error:', error);
        abortController.abort();
    }

  } catch (error) {
      console.error('Error setting up video interceptor:', error);
  }
};
const globalAudioTracks = [];
const handleAudioTrack = async (event) => {
  let lastAudioFormat = null;  // Track last seen format
  
  try {
    // Create processor to get raw frames
    const processor = new MediaStreamTrackProcessor({ track: event.track });
    const generator = new MediaStreamTrackGenerator({ kind: 'audio' });
    
    globalAudioTracks.push(event.track);

    // Get readable stream of audio frames
    const readable = processor.readable;
    const writable = generator.writable;

    const firstStreamId = event.streams[0]?.id;

    // Transform stream to intercept frames
    const transformStream = new TransformStream({
        async transform(frame, controller) {
            if (!frame) {
                return;
            }

            try {
                // Check if controller is still active
                if (controller.desiredSize === null) {
                    frame.close();
                    return;
                }

                // Copy the audio data
                const numChannels = frame.numberOfChannels;
                const numSamples = frame.numberOfFrames;
                const audioData = new Float32Array(numSamples);
                
                // Copy data from each channel
                // If multi-channel, average all channels together
                if (numChannels > 1) {
                    // Temporary buffer to hold each channel's data
                    const channelData = new Float32Array(numSamples);
                    
                    // Sum all channels
                    for (let channel = 0; channel < numChannels; channel++) {
                        frame.copyTo(channelData, { planeIndex: channel });
                        for (let i = 0; i < numSamples; i++) {
                            audioData[i] += channelData[i];
                        }
                    }
                    
                    // Average by dividing by number of channels
                    for (let i = 0; i < numSamples; i++) {
                        audioData[i] /= numChannels;
                    }
                } else {
                    // If already mono, just copy the data
                    frame.copyTo(audioData, { planeIndex: 0 });
                }

                // console.log('frame', frame)
                // console.log('audioData', audioData)

                // Check if audio format has changed
                const currentFormat = {
                    numberOfChannels: 1,
                    originalNumberOfChannels: frame.numberOfChannels,
                    numberOfFrames: frame.numberOfFrames,
                    sampleRate: frame.sampleRate,
                    format: frame.format,
                    duration: frame.duration
                };

                // If format is different from last seen format, send update
                if (!lastAudioFormat || 
                    JSON.stringify(currentFormat) !== JSON.stringify(lastAudioFormat)) {
                    lastAudioFormat = currentFormat;
                    ws.sendJson({
                        type: 'AudioFormatUpdate',
                        format: currentFormat
                    });
                }

                // If the audioData buffer is all zeros, then we don't want to send it
                // Removing this since we implemented 3 audio sources in gstreamer pipeline
                // if (audioData.every(value => value === 0)) {
                //    return;
                // }

                // Send audio data through websocket
                const currentTimeMicros = BigInt(Math.floor(performance.now() * 1000));
                ws.sendAudio(currentTimeMicros, firstStreamId, audioData);

                // Pass through the original frame
                controller.enqueue(frame);
            } catch (error) {
                console.error('Error processing frame:', error);
                frame.close();
            }
        },
        flush() {
            console.log('Transform stream flush called');
        }
    });

    // Create an abort controller for cleanup
    const abortController = new AbortController();

    try {
        // Connect the streams
        await readable
            .pipeThrough(transformStream)
            .pipeTo(writable, {
                signal: abortController.signal
            })
            .catch(error => {
                if (error.name !== 'AbortError') {
                    console.error('Pipeline error:', error);
                }
            });
    } catch (error) {
        console.error('Stream pipeline error:', error);
        abortController.abort();
    }

  } catch (error) {
      console.error('Error setting up audio interceptor:', error);
  }
};

new RTCInterceptor({
    onPeerConnectionCreate: (peerConnection) => {
        console.log('New RTCPeerConnection created:', peerConnection);
        peerConnection.addEventListener('datachannel', (event) => {
            console.log('datachannel', event);
            if (event.channel.label === "collections") {               
                event.channel.addEventListener("message", (messageEvent) => {
                    console.log('RAWcollectionsevent', messageEvent);
                    handleCollectionEvent(messageEvent);
                });
            }
        });

        peerConnection.addEventListener('track', (event) => {
            // Log the track and its associated streams
            if (event.track.kind === 'audio' || event.track.kind === 'video') {
            console.log('New track:', {
                trackId: event.track.id,
                streams: event.streams,
                streamIds: event.streams.map(stream => stream.id),
                // Get any msid information
                transceiver: event.transceiver,
                // Get the RTP parameters which might contain stream IDs
                rtpParameters: event.transceiver?.sender.getParameters()
            });
        }
            if (event.track.kind === 'audio') {
                handleAudioTrack(event);
            }
            if (event.track.kind === 'video') {
                handleVideoTrack(event);
            }
        });

        // Log the signaling state changes
        peerConnection.addEventListener('signalingstatechange', () => {
            console.log('Signaling State:', peerConnection.signalingState);
        });

        // Log the SDP being exchanged
        const originalSetLocalDescription = peerConnection.setLocalDescription;
        peerConnection.setLocalDescription = function(description) {
            console.log('Local SDP:', description);
            return originalSetLocalDescription.apply(this, arguments);
        };

        const originalSetRemoteDescription = peerConnection.setRemoteDescription;
        peerConnection.setRemoteDescription = function(description) {
            console.log('Remote SDP:', description);
            return originalSetRemoteDescription.apply(this, arguments);
        };

        // Log ICE candidates
        peerConnection.addEventListener('icecandidate', (event) => {
            if (event.candidate) {
                console.log('ICE Candidate:', event.candidate);
            }
        });
    },
    onDataChannelCreate: (dataChannel, peerConnection) => {
        console.log('New DataChannel created:', dataChannel);
        console.log('On PeerConnection:', peerConnection);
        console.log('Channel label:', dataChannel.label);

        //if (dataChannel.label === 'collections') {
          //  dataChannel.addEventListener("message", (event) => {
         //       console.log('collectionsevent', event)
        //    });
        //}


      if (dataChannel.label === 'media-director') {
        dataChannel.addEventListener("message", (mediaDirectorEvent) => {
            handleMediaDirectorEvent(mediaDirectorEvent);
        });
      }

       if (dataChannel.label === 'captions') {
            dataChannel.addEventListener("message", (captionEvent) => {
                handleCaptionEvent(captionEvent);
            });
        }
    }
});



// MediaStream interceptor
const globalMediaStreams = [];
class MediaStreamInterceptor {
    constructor() {
        // Store the original MediaStream constructor
        const originalMediaStream = window.MediaStream;
        
        // Override the MediaStream constructor
        window.MediaStream = function(...args) {
            // Create instance using the original constructor
            const mediaStream = Reflect.construct(originalMediaStream, args);
            
            // Add to global array
            globalMediaStreams.push(mediaStream);
            
            console.log(`MediaStream created: ${mediaStream.id}, total streams: ${globalMediaStreams.length}`);
            
            return mediaStream;
        };
        
        // Ensure prototype chain is maintained
        window.MediaStream.prototype = originalMediaStream.prototype;
    }
}

// Initialize the MediaStream interceptor
new MediaStreamInterceptor();

// Helper function to get stream info
window.getMediaStreamInfo = () => {
    return {
        count: globalMediaStreams.length,
        streams: globalMediaStreams,
        tracks: globalMediaStreams.map(s => s.getTracks()),
    };
};

// Add this function for screen recording with audio
async function createScreenRecorder() {
  // Create UI elements
  const recorderContainer = document.createElement('div');
  recorderContainer.style.position = 'fixed';
  recorderContainer.style.top = '10px';
  recorderContainer.style.right = '10px';
  recorderContainer.style.zIndex = '9999';
  recorderContainer.style.background = '#ffffff';
  recorderContainer.style.borderRadius = '8px';
  recorderContainer.style.padding = '10px';
  recorderContainer.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
  
  const buttonBar = document.createElement('div');
  buttonBar.style.display = 'flex';
  buttonBar.style.gap = '10px';
  buttonBar.style.marginBottom = '10px';
  
  const startButton = document.createElement('button');
  startButton.textContent = '⚫ Record Screen';
  startButton.style.padding = '8px 12px';
  startButton.style.background = '#00a2ff';
  startButton.style.color = 'white';
  startButton.style.border = 'none';
  startButton.style.borderRadius = '4px';
  startButton.style.cursor = 'pointer';
  
  const stopButton = document.createElement('button');
  stopButton.textContent = '⏹️ Stop';
  stopButton.style.padding = '8px 12px';
  stopButton.style.background = '#ff4d4d';
  stopButton.style.color = 'white';
  stopButton.style.border = 'none';
  stopButton.style.borderRadius = '4px';
  stopButton.style.cursor = 'pointer';
  stopButton.style.display = 'none';
  
  // Audio options section
  const audioOptionsDiv = document.createElement('div');
  audioOptionsDiv.style.marginBottom = '10px';
  
  const audioOptionsLabel = document.createElement('div');
  audioOptionsLabel.textContent = 'Audio Sources:';
  audioOptionsLabel.style.fontWeight = 'bold';
  audioOptionsLabel.style.marginBottom = '5px';
  
  const systemAudioLabel = document.createElement('label');
  systemAudioLabel.style.display = 'block';
  systemAudioLabel.style.marginBottom = '5px';
  
  const systemAudioCheckbox = document.createElement('input');
  systemAudioCheckbox.type = 'checkbox';
  systemAudioCheckbox.checked = true;
  systemAudioCheckbox.id = 'system-audio';
  
  systemAudioLabel.appendChild(systemAudioCheckbox);
  systemAudioLabel.appendChild(document.createTextNode(' System Audio (Chrome)'));
  
  const micAudioLabel = document.createElement('label');
  micAudioLabel.style.display = 'block';
  
  const micAudioCheckbox = document.createElement('input');
  micAudioCheckbox.type = 'checkbox';
  micAudioCheckbox.id = 'mic-audio';
  
  micAudioLabel.appendChild(micAudioCheckbox);
  micAudioLabel.appendChild(document.createTextNode(' Microphone'));
  
  audioOptionsDiv.appendChild(audioOptionsLabel);
  audioOptionsDiv.appendChild(systemAudioLabel);
  audioOptionsDiv.appendChild(micAudioLabel);
  
  const statusText = document.createElement('div');
  statusText.textContent = 'Ready to record';
  statusText.style.margin = '5px 0';
  
  const previewVideo = document.createElement('video');
  previewVideo.style.width = '240px';
  previewVideo.style.height = '180px';
  previewVideo.style.borderRadius = '4px';
  previewVideo.style.backgroundColor = '#000';
  previewVideo.style.display = 'none';
  previewVideo.controls = true;
  
  const downloadLink = document.createElement('a');
  downloadLink.textContent = '💾 Download Recording';
  downloadLink.style.display = 'none';
  downloadLink.style.textAlign = 'center';
  downloadLink.style.padding = '8px 12px';
  downloadLink.style.background = '#4CAF50';
  downloadLink.style.color = 'white';
  downloadLink.style.borderRadius = '4px';
  downloadLink.style.textDecoration = 'none';
  downloadLink.style.marginTop = '10px';
  
  buttonBar.appendChild(startButton);
  buttonBar.appendChild(stopButton);
  recorderContainer.appendChild(buttonBar);
  recorderContainer.appendChild(audioOptionsDiv);
  recorderContainer.appendChild(statusText);
  recorderContainer.appendChild(previewVideo);
  recorderContainer.appendChild(downloadLink);
  document.body.appendChild(recorderContainer);
  
  // Screen recording functionality
  let mediaRecorder;
  let recordedChunks = [];
  let screenStream;
  let micStream;
  let combinedStream;
  let recordingInterval;
  let startTime;
  
  startButton.addEventListener('click', async () => {
    try {
      const wantSystemAudio = systemAudioCheckbox.checked;
      const wantMicAudio = micAudioCheckbox.checked;
      
      // Get screen capture stream with audio options specific to Chrome
      screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          cursor: "always",
          displaySurface: "browser" // You can also use "window" or "monitor"
        },
        audio: wantSystemAudio ? {
          // Chrome-specific constraints for system audio
          suppressLocalAudioPlayback: false,
          // Ensure we get system audio when available
          audioGainControl: false,
          echoCancellation: false,
          noiseSuppression: false
        } : false
      });
      
      // Check if we got system audio
      const hasSystemAudio = screenStream.getAudioTracks().length > 0;
      if (wantSystemAudio && !hasSystemAudio) {
        statusText.textContent = "Note: System audio not available. Try 'Share tab audio' in Chrome's share dialog.";
      }
      
      // Create the combined stream for recording
      const tracks = [...screenStream.getTracks()];
      
      // Add microphone audio if requested
      if (wantMicAudio) {
        try {
          micStream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true
            }
          });
          tracks.push(...micStream.getAudioTracks());
          statusText.textContent = "Recording with microphone audio";
        } catch (micError) {
          console.error("Could not get microphone:", micError);
          statusText.textContent = "Could not access microphone. Recording without mic.";
        }
      }
      
      // Create a combined stream with all tracks
      combinedStream = new MediaStream(tracks);
      
      // Determine best MIME type for audio+video recording
      const mimeTypes = [
        'video/mp4;codecs=h264,aac',
        'video/mp4;codecs=avc1,mp4a.40.2',
        'video/webm;codecs=vp9,opus', // fallback
      ];
      
      let mimeType = mimeTypes.find(type => MediaRecorder.isTypeSupported(type)) || 'video/mp4';
      console.log('Using MIME type:', mimeType);
      
      // Create the recorder with optimal settings for Chrome
      mediaRecorder = new MediaRecorder(combinedStream, {
        mimeType: mimeType,
        videoBitsPerSecond: 2500000, // 2.5 Mbps
        audioBitsPerSecond: 128000   // 128 kbps
      });
      
      // Setup preview
      previewVideo.srcObject = combinedStream;
      previewVideo.style.display = 'block';
      previewVideo.muted = true; // Avoid echo when recording
      previewVideo.play().catch(e => console.log('Preview play prevented:', e));
      
      // Record data
      recordedChunks = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
          const totalMB = recordedChunks.reduce((size, chunk) => size + chunk.size, 0) / (1024 * 1024);
          statusText.textContent = `Recording: ${Math.floor(totalMB * 100) / 100} MB captured`;
        }
      };
      
      // Start recording
      mediaRecorder.start(1000); // Collect data every second
      startTime = Date.now();
      
      // Update recording time
      recordingInterval = setInterval(() => {
        const duration = Math.floor((Date.now() - startTime) / 1000);
        const minutes = Math.floor(duration / 60).toString().padStart(2, '0');
        const seconds = (duration % 60).toString().padStart(2, '0');
        statusText.textContent = `Recording: ${minutes}:${seconds}`;
      }, 1000);
      
      // Update UI
      startButton.style.display = 'none';
      stopButton.style.display = 'block';
      downloadLink.style.display = 'none';
      audioOptionsDiv.style.display = 'none';
      
      // Handle stream end (when user clicks "Stop sharing")
      screenStream.getVideoTracks()[0].onended = () => {
        stopRecording();
      };
      
    } catch (error) {
      console.error('Error starting screen recording:', error);
      statusText.textContent = `Error: ${error.message}`;
    }
  });
  
  stopButton.addEventListener('click', stopRecording);
  
  function stopRecording() {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') return;
    
    // Stop the recording
    mediaRecorder.stop();
    clearInterval(recordingInterval);
    
    // Stop all tracks
    if (screenStream) {
      screenStream.getTracks().forEach(track => track.stop());
    }
    if (micStream) {
      micStream.getTracks().forEach(track => track.stop());
    }
    
    // Update UI
    startButton.style.display = 'block';
    stopButton.style.display = 'none';
    audioOptionsDiv.style.display = 'block';
    statusText.textContent = 'Processing recording...';
    
    // Handle recording completion
    mediaRecorder.onstop = () => {
      // Create recording blob
      const blob = new Blob(recordedChunks, { type: mediaRecorder.mimeType });
      const url = URL.createObjectURL(blob);
      
      // Update preview video
      previewVideo.srcObject = null;
      previewVideo.src = url;
      previewVideo.muted = false; // Allow audio playback in preview
      
      // Update download link
      downloadLink.href = url;
      downloadLink.download = `screen-recording-${new Date().toISOString().replace(/:/g, '-')}.mp4`;
      downloadLink.style.display = 'block';
      
      // Update status
      const sizeMB = (blob.size / (1024 * 1024)).toFixed(2);
      statusText.textContent = `Recording complete: ${sizeMB} MB`;
    };
  }
  
  return {
    startRecording: () => startButton.click(),
    stopRecording: () => stopButton.click()
  };
}

// Add this to initialize the screen recorder
window.addEventListener('load', () => {
  // Create the screen recorder when the page is fully loaded
  window.screenRecorder = createScreenRecorder();
  
  // You can access it from the console via window.screenRecorder.startRecording() or stopRecording()
});
