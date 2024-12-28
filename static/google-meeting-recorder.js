function onSpeakerIndicatorMutation(indicator) {
    console.log(`onSpeakerIndicatorMutation called for ${indicator.speakerName} (${indicator.key}) (${indicator.data}) at ${Date.now()}`);
}

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
            dataNode: parentElement,
            dataNodeKey: participantDataKey
        };

        participantSpeakingStates.push(speakingState);
    }

    for (const speakingState of participantSpeakingStates) {
        if (speakingState.node.__attendee__hasObserver && 
            speakingState.speakerName === speakingState.node.__attendee__user) {
            continue;
        }

        if (speakingState.node.__attendee__hasObserver && speakingState.node.__attendee__observer) {
            speakingState.node.__attendee__observer.disconnect();
        }

        console.log(`add mutation observer for ${speakingState.speakerName} at ${Date.now()}`);

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