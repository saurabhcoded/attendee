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
        console.log('responseText44', responseText);
        const decodedData = base64ToUint8Array(responseText);
        console.log('decodedData44', decodedData);
        const meetingSpace = MeetingSpaceCollectionResponse.decode(decodedData);
        if (meetingSpace.spaces?.wrapper?.userDetails) {
          for (const user of meetingSpace.spaces.wrapper.userDetails) {
            userMap.set(user.deviceId, {
              id: user.deviceId,
              name: user.name,
              fullName: user.fullName,
              image: user.profile
            });
          }
          console.log('userMap', userMap);
        }   
    }
});

const handleCollectionMessage = (event) => {
    console.log('raw unzipped data', pako.inflate(new Uint8Array(event.data)));
    const unzippedData = protobuf.Reader.create(pako.inflate(new Uint8Array(event.data)));
    const message = CollectionMessage.decode(unzippedData);
    console.log('decodedmessage', message);
    if (message?.body?.wrapper?.wrapper.wrapper?.userDetails) {
        const users = message.body.wrapper.wrapper.wrapper.userDetails;
        console.log('users', users);
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

new RTCInterceptor({
    onPeerConnectionCreate: (peerConnection) => {
        console.log('New RTCPeerConnection created:', peerConnection);
        peerConnection.addEventListener('datachannel', (event) => {
            console.log('datachannel', event)
            if (event.channel.label === "collections") {               
                event.channel.addEventListener("message", (messageEvent) => {
                    console.log('collectionsevent', messageEvent)
                    handleCollectionMessage(messageEvent);
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