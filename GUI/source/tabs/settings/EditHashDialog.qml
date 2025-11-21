import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3

// Dialog for editing model hash and metadata
Dialog {
    id: editHashDialog
    
    property var modelInfo: null
    property string modelPath: ""
    
    signal hashChanged(string hash, string hashType)
    
    title: "Edit Model Hash"
    width: 500
    height: 400
    
    onAccepted: saveChanges()
    
    function show(path, info) {
        modelPath = path
        modelInfo = info
        
        modelNameText.text = info.name
        hashInput.text = info.hash
        hashTypeCombo.currentIndex = hashTypeCombo.find(info.hashType)
        civitaiUrlInput.text = ""
        statusText.text = ""
        
        open()
    }
    
    function saveChanges() {
        if (!hashInput.text.trim()) {
            statusText.text = "Hash cannot be empty"
            statusText.color = "#ff6666"
            return
        }
        
        hashChanged(hashInput.text, hashTypeCombo.currentText)
        statusText.text = "Hash saved successfully"
        statusText.color = "#66ff66"
    }
    
    contentItem: Rectangle {
        color: "#2a2a2a"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 12
            
            // Model info
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                
                Text {
                    text: "Model:"
                    color: "#ffffff"
                    font.bold: true
                    font.pixelSize: 12
                }
                
                Text {
                    id: modelNameText
                    Layout.fillWidth: true
                    color: "#aaaaaa"
                    font.pixelSize: 11
                    wrapMode: Text.Wrap
                }
            }
            
            Separator {
                Layout.fillWidth: true
            }
            
            // Hash section
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 8
                
                Text {
                    text: "Hash Information"
                    color: "#ffffff"
                    font.bold: true
                    font.pixelSize: 12
                }
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        
                        Text {
                            text: "Hash:"
                            color: "#aaaaaa"
                            font.pixelSize: 10
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            height: 32
                            color: "#1a1a1a"
                            border.color: "#444"
                            radius: 4
                            
                            TextInput {
                                id: hashInput
                                anchors.fill: parent
                                anchors.margins: 8
                                color: "#00cc00"
                                font.family: "Courier New"
                                font.pixelSize: 11
                                selectByMouse: true
                            }
                        }
                    }
                    
                    ColumnLayout {
                        Layout.preferredWidth: 120
                        spacing: 4
                        
                        Text {
                            text: "Type:"
                            color: "#aaaaaa"
                            font.pixelSize: 10
                        }
                        
                        ComboBox {
                            id: hashTypeCombo
                            Layout.fillWidth: true
                            model: ["AUTOV2", "SHA256", "civitai", "legacy"]
                            
                            background: Rectangle {
                                color: "#1a1a1a"
                                border.color: "#444"
                                radius: 4
                            }
                            
                            contentItem: Text {
                                color: "#aaaaaa"
                                text: hashTypeCombo.displayText
                                leftPadding: 8
                                verticalAlignment: Text.AlignVCenter
                            }
                            
                            popup: Popup {
                                y: hashTypeCombo.height
                                width: hashTypeCombo.width
                                implicitHeight: contentItem.implicitHeight + 10
                                
                                background: Rectangle {
                                    color: "#1a1a1a"
                                    border.color: "#444"
                                }
                                
                                contentItem: ListView {
                                    model: hashTypeCombo.model
                                    delegate: ItemDelegate {
                                        width: parent.width
                                        text: modelData
                                        background: Rectangle {
                                            color: hovered ? "#333" : "#1a1a1a"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            Separator {
                Layout.fillWidth: true
            }
            
            // Civitai URL input
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 8
                
                Text {
                    text: "Or fetch from Civitai"
                    color: "#ffffff"
                    font.bold: true
                    font.pixelSize: 12
                }
                
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    
                    Text {
                        text: "Civitai URL or Model ID:"
                        color: "#aaaaaa"
                        font.pixelSize: 10
                    }
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: 32
                        color: "#1a1a1a"
                        border.color: "#444"
                        radius: 4
                        
                        TextInput {
                            id: civitaiUrlInput
                            anchors.fill: parent
                            anchors.margins: 8
                            color: "#aaaaaa"
                            font.pixelSize: 11
                            selectByMouse: true
                            placeholderText: "e.g., https://civitai.com/models/123456 or 123456"
                        }
                    }
                }
                
                Button {
                    Layout.fillWidth: true
                    text: "Fetch from Civitai"
                    enabled: civitaiUrlInput.text.trim().length > 0
                    
                    onClicked: {
                        statusText.text = "Fetching from Civitai..."
                        statusText.color = "#ffcc00"
                        // This will be connected to ModelManager.fetch_civitai_metadata in Python
                    }
                }
            }
            
            Separator {
                Layout.fillWidth: true
            }
            
            // Status message
            Text {
                id: statusText
                Layout.fillWidth: true
                color: "#aaaaaa"
                font.pixelSize: 10
                wrapMode: Text.Wrap
            }
            
            Item {
                Layout.fillHeight: true
            }
            
            // Buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 8
                
                Item {
                    Layout.fillWidth: true
                }
                
                Button {
                    text: "Cancel"
                    onClicked: editHashDialog.reject()
                }
                
                Button {
                    text: "Save"
                    onClicked: editHashDialog.accept()
                }
            }
        }
    }
}

// Separator component
Rectangle {
    id: separator
    color: "#444"
    height: 1
}
