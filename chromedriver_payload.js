// User manager
class UserManager {
    constructor(ws) {
        this.allUsersMap = new Map();
        this.currentUsersMap = new Map();
        this.ws = ws;
    }

    singleUserSynced(user) {
      // Create array with new user and existing users, then filter for unique deviceIds
      // keeping the first occurrence (new user takes precedence)
      const allUsers = [user, ...this.currentUsersMap.values()];
      const uniqueUsers = Array.from(
        new Map(allUsers.map(user => [user.deviceId, user])).values()
      );
      this.newUsersListSynced(uniqueUsers);
    }

    newUsersListSynced(newUsersList) {
        // Get the current user IDs before updating
        const previousUserIds = new Set(this.currentUsersMap.keys());
        const newUserIds = new Set(newUsersList.map(user => user.deviceId));

        // Update all users map
        for (const user of newUsersList) {
            this.allUsersMap.set(user.deviceId, {
                deviceId: user.deviceId,
                displayName: user.displayName,
                fullName: user.fullName,
                profile: user.profile
            });
        }

        // Calculate joined and left users
        const joined = newUsersList.filter(user => !previousUserIds.has(user.deviceId));
        const left = Array.from(previousUserIds)
            .filter(id => !newUserIds.has(id))
            .map(id => this.currentUsersMap.get(id));

        // Clear current users map and update with new list
        this.currentUsersMap.clear();
        for (const user of newUsersList) {
            this.currentUsersMap.set(user.deviceId, {
                deviceId: user.deviceId,
                displayName: user.displayName,
                fullName: user.fullName,
                profile: user.profile
            });
        }

        this.ws.sendJson({
            type: 'UsersUpdate',
            joined: joined,
            left: left
        });
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

  constructor(url = 'ws://localhost:8765') {
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

// Protobuf decoders
class CollectionMessage {
    constructor() {
      this.body = null; // Contains CollectionMessageBody
    }
  
    // Decodes a CollectionMessage from a Uint8Array of protobuf bytes
    static decode(reader, length) {
      // If we don't have a proper reader, create one
      if (!(reader instanceof protobuf.Reader)) {
        reader = protobuf.Reader.create(reader);
      }
  
      // Get the length of data to read
      const end = length === undefined ? reader.len : reader.pos + length;
      
      // Create a new message instance
      const message = new CollectionMessage();
  
      // Read fields until we reach the end
      while (reader.pos < end) {
        // Get the field number and wire type
        const tag = reader.uint32();
        
        switch (tag >>> 3) { // Field number
          case 1: // body field
            message.body = CollectionMessageBody.decode(reader, reader.uint32());
            break;
          default:
            reader.skipType(tag & 7); // Skip unknown fields
        }
      }
  
      return message;
    }
  }
  
  class CollectionMessageBody {
    constructor() {
      this.wrapper = null; // Contains Wrapper1
    }
  
    static decode(reader, length) {
      if (!(reader instanceof protobuf.Reader)) {
        reader = protobuf.Reader.create(reader);
      }
  
      const end = length === undefined ? reader.len : reader.pos + length;
      const message = new CollectionMessageBody();
  
      while (reader.pos < end) {
        const tag = reader.uint32();
        
        switch (tag >>> 3) {
          case 2: // wrapper field
            message.wrapper = Wrapper1.decode(reader, reader.uint32());
            break;
          default:
            reader.skipType(tag & 7);
        }
      }
  
      return message;
    }
  }
  
  class Wrapper1 {
    constructor() {
      this.wrapper = null; // Contains Wrapper2
    }
  
    static decode(reader, length) {
      if (!(reader instanceof protobuf.Reader)) {
        reader = protobuf.Reader.create(reader);
      }
  
      const end = length === undefined ? reader.len : reader.pos + length;
      const message = new Wrapper1();
  
      while (reader.pos < end) {
        const tag = reader.uint32();
        
        switch (tag >>> 3) {
          case 13: // wrapper field
            message.wrapper = Wrapper2.decode(reader, reader.uint32());
            break;
          default:
            reader.skipType(tag & 7);
        }
      }
  
      return message;
    }
  }
  
  class Wrapper2 {
    constructor() {
      this.wrapper = null; // Contains Wrapper3
      this.chat = []; // Array of ChatWrapper
    }
  
    static decode(reader, length) {
      if (!(reader instanceof protobuf.Reader)) {
        reader = protobuf.Reader.create(reader);
      }
  
      const end = length === undefined ? reader.len : reader.pos + length;
      const message = new Wrapper2();
  
      while (reader.pos < end) {
        const tag = reader.uint32();
        
        switch (tag >>> 3) {
          case 1: // wrapper field
            message.wrapper = Wrapper3.decode(reader, reader.uint32());
            break;
          case 4: // chat field
            if (!message.chat) {
              message.chat = [];
            }
            message.chat.push(ChatWrapper.decode(reader, reader.uint32()));
            break;
          default:
            reader.skipType(tag & 7);
        }
      }
  
      return message;
    }
  }
  
  class Wrapper3 {
    constructor() {
      this.userDetails = []; // Array of UserDetails
    }
  
    static decode(reader, length) {
      if (!(reader instanceof protobuf.Reader)) {
        reader = protobuf.Reader.create(reader);
      }
  
      const end = length === undefined ? reader.len : reader.pos + length;
      const message = new Wrapper3();
  
      while (reader.pos < end) {
        const tag = reader.uint32();
        
        switch (tag >>> 3) {
          case 2: // userDetails field
            if (!message.userDetails) {
              message.userDetails = [];
            }
            message.userDetails.push(UserDetails.decode(reader, reader.uint32()));
            break;
          default:
            reader.skipType(tag & 7);
        }
      }
  
      return message;
    }
  }

class UserDetails {
    constructor() {
      this.deviceId = "";
      this.fullName = "";
      this.profile = "";
      this.name = "";
    }
  
    static decode(reader, length) {
      if (!(reader instanceof protobuf.Reader)) {
        reader = protobuf.Reader.create(reader);
      }
  
      const end = length === undefined ? reader.len : reader.pos + length;
      const message = new UserDetails();
  
      while (reader.pos < end) {
        const tag = reader.uint32();
        
        switch (tag >>> 3) {
          case 1:
            message.deviceId = reader.string();
            break;
          case 2:
            message.fullName = reader.string();
            break;
          case 3:
            message.profile = reader.string();
            break;
          case 29:
            message.name = reader.string();
            break;
          default:
            reader.skipType(tag & 7);
        }
      }
  
      return message;
    }
  }

class UserDetailsWrapper {
    constructor() {
        this.userDetails = []; // Array of UserDetails
    }

    static decode(reader, length) {
        if (!(reader instanceof protobuf.Reader)) {
            reader = protobuf.Reader.create(reader);
        }

        const end = length === undefined ? reader.len : reader.pos + length;
        const message = new UserDetailsWrapper();

        while (reader.pos < end) {
            const tag = reader.uint32();
            
            switch (tag >>> 3) {
                case 2: // userDetails field
                    if (!message.userDetails) {
                        message.userDetails = [];
                    }
                    message.userDetails.push(UserDetails.decode(reader, reader.uint32()));
                    break;
                default:
                    reader.skipType(tag & 7);
            }
        }

        return message;
    }
}

class SpaceCollection {
    constructor() {
        this.wrapper = null; // Contains UserDetailsWrapper
    }

    static decode(reader, length) {
        if (!(reader instanceof protobuf.Reader)) {
            reader = protobuf.Reader.create(reader);
        }

        const end = length === undefined ? reader.len : reader.pos + length;
        const message = new SpaceCollection();

        while (reader.pos < end) {
            const tag = reader.uint32();
            
            switch (tag >>> 3) {
                case 2: // wrapper field
                    message.wrapper = UserDetailsWrapper.decode(reader, reader.uint32());
                    break;
                default:
                    reader.skipType(tag & 7);
            }
        }

        return message;
    }
}

class MeetingSpaceCollectionResponse {
    constructor() {
        this.spaces = null; // Contains SpaceCollection
    }

    static decode(reader, length) {
        if (!(reader instanceof protobuf.Reader)) {
            reader = protobuf.Reader.create(reader);
        }

        const end = length === undefined ? reader.len : reader.pos + length;
        const message = new MeetingSpaceCollectionResponse();

        while (reader.pos < end) {
            const tag = reader.uint32();
            
            switch (tag >>> 3) {
                case 2: // spaces field
                    message.spaces = SpaceCollection.decode(reader, reader.uint32());
                    break;
                default:
                    reader.skipType(tag & 7);
            }
        }

        return message;
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
            { name: 'userInfoListWrapperAndChatWrapper', fieldNumber: 13, type: 'message', messageType: 'UserInfoListWrapperAndChatWrapper' }
        ]
    },
    {
        name: 'UserInfoListWrapperAndChatWrapper',
        fields: [
            { name: 'userInfoListWrapper', fieldNumber: 1, type: 'message', messageType: 'UserInfoListWrapper' },
            // { name: 'chat', fieldNumber: 4, type: 'message', messageType: 'ChatMessage', repeated: true }
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
        name: 'UserInfoListWrapper',
        fields: [
            { name: 'userInfoList', fieldNumber: 2, type: 'message', messageType: 'UserInfoList', repeated: true }
        ]
    },
    {
        name: 'UserInfoList',
        fields: [
            { name: 'deviceId', fieldNumber: 1, type: 'string' },
            { name: 'fullName', fieldNumber: 2, type: 'string' },
            { name: 'profilePicture', fieldNumber: 3, type: 'string' },
            { name: 'displayName', fieldNumber: 29, type: 'string' }
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
const userManager = new UserManager(ws);

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

  const collectionEvent = messageDecoders['CollectionEvent'](decodedData);
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

new RTCInterceptor({
    onPeerConnectionCreate: (peerConnection) => {
        console.log('New RTCPeerConnection created:', peerConnection);
        peerConnection.addEventListener('datachannel', (event) => {
            console.log('datachannel', event)
            if (event.channel.label === "collections") {               
                event.channel.addEventListener("message", (messageEvent) => {
                    console.log('collectionsevent', messageEvent)
                    handleCollectionEvent(messageEvent);
                });
            }
        });
    },
    onDataChannelCreate: (dataChannel, peerConnection) => {
        console.log('New DataChannel created:', dataChannel);
        console.log('On PeerConnection:', peerConnection);
        console.log('Channel label:', dataChannel.label);

        if (dataChannel.label === 'collections') {
            dataChannel.addEventListener("message", (event) => {
                console.log('collectionsevent', event)
            });
        }
    }
});