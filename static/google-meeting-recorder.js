function onSpeakerIndicatorMutation(indicator) {
    console.log(`onSpeakerIndicatorMutation called for ${indicator.speakerName} (${indicator.key}) (${indicator.data}) at ${Date.now()}`);
}

const participantListItemSelector = "div[class^='cxdMu']";
const speakerIndicatorSelector = "div[class^='IisKdb']";
const participantNameSelector = "span[class^='zWGUib']";
const participantListSelector = "div[class^='AE8xFb']";

let participantListObserver = null;

function initializeParticipantListObserver() {
    if (participantListObserver) {
        participantListObserver.disconnect();
        participantListObserver = null;
    }

    const listObserver = new MutationObserver(() => {
        updateParticipantListItemObservers();
    });

    const participantListElement = document.querySelector(participantListSelector);
    if (!participantListElement) {
        throw new Error("Unable to find participant list element");
    }

    const observerConfig = {
        childList: true,
        subtree: true,
        attributes: false
    };

    // Initialize the list item observers
    updateParticipantListItemObservers();

    listObserver.observe(participantListElement, observerConfig);
    participantListObserver = listObserver;
}

function updateParticipantListItemObservers() {
    console.log("updateParticipantListItemObservers called");
    
    // Get the participant list container
    const participantListElement = document.querySelector(participantListSelector);
    if (!participantListElement) {
        console.error("Participant list element not found");
        return;
    }

    // Find all participant list items
    const participantItems = participantListElement.querySelectorAll(participantListItemSelector);
    
    participantItems.forEach(item => {
        // Find speaker indicator and name elements for this participant
        const speakerIndicator = item.querySelector(speakerIndicatorSelector);
        const nameElement = item.querySelector(participantNameSelector);
        
        if (!speakerIndicator) {
            console.warn("Missing speaker indicator for participant");
            return;
        }
        if (!nameElement) {
            console.warn("Missing name element for participant"); 
            return;
        }

        // Skip if we already have an observer for this participant
        if (speakerIndicator.__hasObserver) {
            return;
        }

        // Create mutation observer for the speaker indicator
        const observer = new MutationObserver(() => {
            onSpeakerIndicatorMutation({
                speakerName: nameElement.textContent,
                key: speakerIndicator.getAttribute("class"),
                data: speakerIndicator.getAttribute("data-participant-id") || "",
                node: speakerIndicator
            });
        });

        // Observe only attribute changes
        observer.observe(speakerIndicator, {
            attributes: true,
            subtree: false,
            childList: false
        });

        // Mark this indicator as having an observer
        speakerIndicator.__hasObserver = true;
        speakerIndicator.__observer = observer;
    });
}

const initializeCaptionProxy = () => {
    if (!window.proxyPeerConnection) {
        return;
    }
    
    isCapturing = false;
    
    // Create data channel for captions with ordered delivery
    window.proxyPeerConnection.createDataChannel("captions", {
        ordered: true,
        maxRetransmits: 100,
        id: channelId++
    });
};

initializeParticipantListObserver();

/*
onSpeakerIndicatorMutation called for Noah Duncan (Hzro4b6:gMRytd6:u0RICc6:mBKYYd6:Bq1x4c6:fJKVEb27:speakerAwareVolumeIndicator) (spaces/7e0kde1DrcQB/devices/3ccbdd8f-f36e-4eac-a8f6-80e3db9b6569,https://lh3.googleusercontent.com/a/ACg8ocJTD-7OUJpzDQSAxFd8nWOJjofH-GRHGKCfcOZgvceJYZys=s192-c-mo,0,false,true,false,false,true,false,,,false,false,false,true,false,false,,,,,,,,,,,2,Noah Duncan,5,,,true,true,0.8,1735359289477,true,Noah,,,,,,false,0,0,true,0,1,,tU2nvcckeEXOXoK3y4RSj6AZrya3Gd2SFw7wqcJUoY4=,,1,,,,,false,true,0,false,0,false,2,,0,,true,,0,true,,true,,,,false,true,noah duncan,false) at 1735359306408
*/
/*
onSpeakerIndicatorMutation called for Noah Duncan (Hzro4b6:gMRytd6:u0RICc6:mBKYYd6:Bq1x4c6:fJKVEb27:speakerAwareVolumeIndicator) (spaces/7e0kde1DrcQB/devices/ecac05b4-7dcd-4325-90b0-d3032a42072a,https://lh3.googleusercontent.com/a/ACg8ocJTD-7OUJpzDQSAxFd8nWOJjofH-GRHGKCfcOZgvceJYZys=s192-c-mo,0,false,true,false,false,true,false,,,false,false,false,true,false,false,,,,,,,,,,,2,Noah Duncan,5,,,true,true,0.6,1735359200716,false,Noah,,,,,,false,0,0,true,0,1,,tU2nvcckeEXOXoK3y4RSj6AZrya3Gd2SFw7wqcJUoY4=,,1,,,,,false,true,0,false,0,false,2,,0,,true,,0,true,,true,,,,false,true,noah duncan,false) at 1735359245825
*/
/*
onSpeakerIndicatorMutation called for Bob Chump (Hzro4b6:m7YTAe6:Bq1x4c6:fJKVEb27:speakerAwareVolumeIndicator) (spaces/7e0kde1DrcQB/devices/f21cd9e3-90b0-47f8-bf19-0ebe72e05576,https://lh3.googleusercontent.com/mm/ALrkI7p-QU2OpkFmT2XUEB3dQf3c6wEQbugZr3jFMjbbrb03tXWMTG2d1RnSiM-u5nDjUuUDnA,0,true,true,true,true,false,false,,,false,false,false,false,false,true,,,,,,,,,,,2,Bob Chump,5,,,false,false,0,,,,,,,,,false,0,0,false,1,1,,,,3,,,,,false,true,0,false,0,false,2,,0,,true,,0,true,,true,,,,,true,bob chump,false) at 1735359381414
*/
/*
onSpeakerIndicatorMutation called for Noah Duncan (Hzro4b6:m7YTAe6:Bq1x4c6:fJKVEb27:speakerAwareVolumeIndicator) (spaces/7e0kde1DrcQB/devices/cd032771-80de-4d43-b67c-121a3f3b9865,https://lh3.googleusercontent.com/a/ACg8ocJ4MQbgxbO4Ntr0dmPTZmu4YsI5l99hA8Mx4MqcUb1gciOlrw=s192-c-mo,0,false,true,true,true,false,false,,,false,false,false,false,false,true,,,,,,,,,,,2,Noah Duncan,5,,,false,false,0,,,Noah,,,,,,false,0,0,false,0,1,,7cOioJ6lJ15eYXG8UPKd2GjzrTJutiKCqxZ_6xvMraI=,,3,,,,,false,true,0,false,0,false,2,,0,,true,,0,true,,true,,,,,true,noah duncan,false) at 1735359506433
*/
/*
const meetLayoutObserver = null;
const meetGridSelector = "div[class^='axUSnc']";

async function initializeMeetLayoutObserver() {
    if (meetLayoutObserver) {
        meetLayoutObserver.disconnect();
        meetLayoutObserver = null;
    }

    const layoutChangeObserver = new MutationObserver(() => {
        updateParticipantSpeakingObservers();
    });

    const meetGridElement = document.querySelector(meetGridSelector);

    const observerConfig = {
        childList: true,
        subtree: true,
        attributes: false
    };

    if (!meetGridElement) {
        throw new Error("Unable to find Meet video grid element");
    }

    await updateParticipantSpeakingObservers();

    layoutChangeObserver.observe(meetGridElement, observerConfig);
    
    meetLayoutObserver = layoutChangeObserver;
}

async function updateParticipantSpeakingObservers() {
    const speakingIndicatorElements = Array.from(document.getElementsByTagName("div"))
        .filter(element => {
            return element.getAttribute("jscontroller") && 
                   element.__soy && 
                   element.__soy.key.includes("speakerAware") && 
                   element.children.length === 3 && 
                   !element.firstChild?.hasChildNodes() && 
                   !element.lastChild?.hasChildNodes();
        });

    const participantSpeakingStates = [];

    for (const indicatorElement of speakingIndicatorElements) {
        let parentElement = indicatorElement.parentNode;
        let participantDataKey = "";

        while (parentElement) {
            const templateData = parentElement.__soy?.data;
            if (!templateData) {
                parentElement = parentElement.parentNode;
                continue;
            }

            for (const key of Object.keys(templateData)) {
                if (typeof templateData[key] !== "object") {
                    continue;
                }
                participantDataKey = key;
                break;
            }

            if (participantDataKey) break;
            parentElement = parentElement.parentNode;
        }

        if (!participantDataKey || !parentElement) {
            throw new Error("Failed to find participant data key");
        }

        const participantSpace = parentElement.__soy.data[participantDataKey];
        const spaceIdentifier = Object.keys(participantSpace)[0];
        const participantData = participantSpace[spaceIdentifier];
        const participantName = participantData[28];

        if (!participantName) continue;

        const speakingState = {
            key: indicatorElement.__soy.key,
            speakerName: participantName,
            node: indicatorElement,
            data: participantData,
        };

        participantSpeakingStates.push(speakingState);
    }

    for (const speakingState of participantSpeakingStates) {
        if (speakingState.node.__attendee__hasObserver && speakingState.node.__attendee__observer && 
            speakingState.speakerName === speakingState.node.__attendee__user) {
            continue;
        }

        if (speakingState.node.__attendee__hasObserver && speakingState.node.__attendee__observer) {
            speakingState.node.__attendee__observer.disconnect();
        }

        console.log(`add mutation observer for ${speakingState.speakerName}`);

        const speakingStateObserver = new MutationObserver(() => {
            onSpeakerIndicatorMutation(speakingState);
        });

        speakingStateObserver.observe(speakingState.node, {
            attributes: true,
            subtree: false,
            childList: false
        });

        speakingState.node.__attendee__hasObserver = true;
        speakingState.node.__attendee__observer = speakingStateObserver;
        speakingState.node.__attendee__user = speakingState.speakerName;
    }
}

initializeMeetLayoutObserver();
*/