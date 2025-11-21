import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

// Model card component for displaying model information
Rectangle {
    id: modelCard
    
    property var modelInfo: null
    property string displayName: modelInfo ? modelInfo.name : "Unknown"
    property string displayHash: modelInfo ? modelInfo.hash : "No hash"
    property string displayType: modelInfo ? modelInfo.civitaiType : "Unknown"
    property string previewImagePath: modelInfo ? modelInfo.previewPath : ""
    property var triggerWordsList: modelInfo ? modelInfo.triggerWords : []
    
    signal clicked()
    signal editHashClicked()
    signal fetchMetadataClicked()
    
    color: "#2a2a2a"
    radius: 8
    border.color: "#444"
    border.width: 1
    
    width: 250
    height: 380
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onClicked: modelCard.clicked()
        
        onEntered: {
            modelCard.border.color = "#666"
            modelCard.color = "#333333"
        }
        onExited: {
            modelCard.border.color = "#444"
            modelCard.color = "#2a2a2a"
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8
        
        // Preview image
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 140
            color: "#1a1a1a"
            radius: 4
            border.color: "#444"
            
            Image {
                anchors.fill: parent
                anchors.margins: 1
                source: previewImagePath ? "file:///" + previewImagePath : ""
                fillMode: Image.PreserveAspectCrop
                sourceSize: Qt.size(width, height)
                
                Text {
                    anchors.centerIn: parent
                    text: "No preview"
                    color: "#888"
                    visible: parent.status === Image.Null || parent.status === Image.Error
                }
            }
        }
        
        // Model name
        Text {
            Layout.fillWidth: true
            text: displayName
            color: "#ffffff"
            font.pixelSize: 14
            font.bold: true
            elide: Text.ElideRight
            wrapMode: Text.Wrap
            maximumLineCount: 2
        }
        
        // Model type and info
        RowLayout {
            Layout.fillWidth: true
            spacing: 6
            
            Rectangle {
                Layout.preferredWidth: contentText.contentWidth + 8
                Layout.preferredHeight: 20
                color: "#444"
                radius: 3
                
                Text {
                    id: contentText
                    anchors.centerIn: parent
                    text: displayType
                    color: "#aaa"
                    font.pixelSize: 11
                }
            }
        }
        
        // Hash display
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: "#1a1a1a"
            radius: 4
            border.color: "#444"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 6
                spacing: 2
                
                Text {
                    text: "Hash:"
                    color: "#888"
                    font.pixelSize: 10
                }
                
                Text {
                    Layout.fillWidth: true
                    text: displayHash
                    color: "#00cc00"
                    font.pixelSize: 11
                    font.family: "Courier New"
                    elide: Text.ElideRight
                }
            }
        }
        
        // Trigger words (if available)
        Rectangle {
            visible: triggerWordsList.length > 0
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            color: "#1a1a1a"
            radius: 4
            border.color: "#444"
            
            FlowLayout {
                anchors.fill: parent
                anchors.margins: 6
                spacing: 4
                
                Repeater {
                    model: Math.min(3, triggerWordsList.length)
                    
                    Rectangle {
                        color: "#333"
                        radius: 3
                        width: triggerText.contentWidth + 8
                        height: 22
                        
                        Text {
                            id: triggerText
                            anchors.centerIn: parent
                            text: triggerWordsList[index]
                            color: "#99ff99"
                            font.pixelSize: 9
                        }
                    }
                }
                
                Text {
                    visible: triggerWordsList.length > 3
                    text: "+%1 more".arg(triggerWordsList.length - 3)
                    color: "#888"
                    font.pixelSize: 9
                }
            }
        }
        
        Item {
            Layout.fillHeight: true
        }
        
        // Action buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: 6
            
            Button {
                Layout.fillWidth: true
                text: "Edit Hash"
                font.pixelSize: 11
                onClicked: modelCard.editHashClicked()
            }
            
            Button {
                Layout.fillWidth: true
                text: "Fetch"
                font.pixelSize: 11
                onClicked: modelCard.fetchMetadataClicked()
            }
        }
    }
}
