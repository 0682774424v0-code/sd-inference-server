import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

// Вікно з деталями моделі (хеші, метадані, тригер слова)
Popup {
    id: modelDetails
    width: parent.width * 0.8
    height: parent.height * 0.8
    anchors.centerIn: parent
    modal: true
    
    property var modelData: ({})
    
    background: Rectangle {
        color: COMMON.bg1
        border.color: COMMON.bg3
        border.width: 2
        radius: 4
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12
        
        // Заголовок
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            
            // Превью
            Rectangle {
                Layout.preferredWidth: 120
                Layout.preferredHeight: 120
                color: COMMON.bg2
                border.color: COMMON.bg3
                border.width: 1
                radius: 4
                
                Image {
                    anchors.fill: parent
                    anchors.margins: 2
                    source: modelDetails.modelData.preview || ""
                    fillMode: Image.PreserveAspectCrop
                    smooth: true
                }
                
                Text {
                    anchors.centerIn: parent
                    text: "🖼️"
                    font.pixelSize: 48
                    visible: !modelDetails.modelData.preview
                }
            }
            
            // Основна інформація
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                
                Text {
                    text: modelDetails.modelData.name || "Unknown Model"
                    font.pixelSize: 14
                    font.bold: true
                    color: COMMON.fg1
                    wrapMode: Text.WordWrap
                }
                
                Text {
                    text: (modelDetails.modelData.type || "Unknown") + " • " + 
                          (modelDetails.modelData.filename || "")
                    font.pixelSize: 10
                    color: COMMON.fg2
                    wrapMode: Text.WordWrap
                }
                
                Text {
                    text: {
                        let size = modelDetails.modelData.size || 0
                        if (size > 1024*1024*1024) {
                            return (size / (1024*1024*1024)).toFixed(2) + " GB"
                        } else if (size > 1024*1024) {
                            return (size / (1024*1024)).toFixed(1) + " MB"
                        }
                        return size + " B"
                    }
                    font.pixelSize: 9
                    color: COMMON.fg3
                }
                
                if (modelDetails.modelData.author) {
                    Text {
                        text: "By: " + modelDetails.modelData.author
                        font.pixelSize: 10
                        color: COMMON.fg2
                    }
                }
            }
        }
        
        // Розділювач
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: COMMON.bg3
        }
        
        // Хеші
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4
            
            Text {
                text: "Model Hashes (Civitai Format)"
                font.pixelSize: 12
                font.bold: true
                color: COMMON.fg1
            }
            
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                color: COMMON.bg2
                border.color: COMMON.bg3
                border.width: 1
                radius: 2
                
                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 4
                    
                    Column {
                        width: parent.width - 8
                        spacing: 4
                        
                        Repeater {
                            model: {
                                let hashes = modelDetails.modelData.hashes || {}
                                let result = []
                                
                                if (hashes.autov2) result.push({label: "AUTOV2", value: hashes.autov2})
                                if (hashes.sha256) result.push({label: "SHA256", value: hashes.sha256})
                                if (hashes.crc32) result.push({label: "CRC32", value: hashes.crc32})
                                if (hashes.blake3) result.push({label: "BLAKE3", value: hashes.blake3})
                                if (hashes.autov3) result.push({label: "AUTOV3", value: hashes.autov3})
                                
                                return result
                            }
                            
                            delegate: RowLayout {
                                width: parent.width
                                spacing: 8
                                
                                Text {
                                    text: modelData.label + ":"
                                    font.pixelSize: 9
                                    font.bold: true
                                    color: COMMON.fg1
                                    Layout.preferredWidth: 70
                                }
                                
                                Text {
                                    text: modelData.value
                                    font.pixelSize: 9
                                    font.family: "Courier"
                                    color: COMMON.fg2
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                    
                                    MouseArea {
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            // Копіюємо в буфер обміну
                                            // TODO: Реалізувати копіювання
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Теги/Слова-тригери
        if (modelDetails.modelData.trigger_words && modelDetails.modelData.trigger_words.length > 0) {
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                
                Text {
                    text: "Trigger Words"
                    font.pixelSize: 12
                    font.bold: true
                    color: COMMON.fg1
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 80
                    color: COMMON.bg2
                    border.color: COMMON.bg3
                    border.width: 1
                    radius: 2
                    
                    ScrollView {
                        anchors.fill: parent
                        anchors.margins: 4
                        
                        Flow {
                            width: parent.width - 8
                            spacing: 6
                            
                            Repeater {
                                model: modelDetails.modelData.trigger_words || []
                                
                                delegate: Rectangle {
                                    width: triggerText.width + 12
                                    height: 24
                                    color: COMMON.accent
                                    radius: 12
                                    
                                    Text {
                                        id: triggerText
                                        anchors.centerIn: parent
                                        text: modelData
                                        font.pixelSize: 10
                                        color: "white"
                                    }
                                    
                                    MouseArea {
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            // Копіюємо тригер
                                        }
                                        onEntered: parent.color = Qt.lighter(COMMON.accent, 1.2)
                                        onExited: parent.color = COMMON.accent
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Опис
        if (modelDetails.modelData.description) {
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                
                Text {
                    text: "Description"
                    font.pixelSize: 12
                    font.bold: true
                    color: COMMON.fg1
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 80
                    color: COMMON.bg2
                    border.color: COMMON.bg3
                    border.width: 1
                    radius: 2
                    
                    ScrollView {
                        anchors.fill: parent
                        anchors.margins: 4
                        
                        Text {
                            width: parent.width - 8
                            text: modelDetails.modelData.description
                            font.pixelSize: 10
                            color: COMMON.fg2
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }
        
        Item { Layout.fillHeight: true }
        
        // Кнопки
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            
            Item { Layout.fillWidth: true }
            
            Button {
                text: "Close"
                Layout.preferredWidth: 100
                Layout.preferredHeight: 32
                
                background: Rectangle {
                    color: COMMON.bg2
                    border.color: COMMON.bg3
                    border.width: 1
                    radius: 2
                }
                
                contentItem: Text {
                    text: parent.text
                    color: COMMON.fg1
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.bold: true
                }
                
                onClicked: modelDetails.close()
            }
        }
    }
}
