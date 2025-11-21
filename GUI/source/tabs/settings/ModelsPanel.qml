import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3

// Main models panel for viewing and managing models
Rectangle {
    id: modelsPanel
    
    color: "#1f1f1f"
    
    property string currentFolder: ""
    property var modelManager: null
    
    function loadModelsFromFolder(folderPath) {
        currentFolder = folderPath
        if (modelManager) {
            modelManager.load_models_from_folder(folderPath)
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12
        
        // Header
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            
            Text {
                text: "Model Library"
                color: "#ffffff"
                font.pixelSize: 18
                font.bold: true
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            Text {
                id: modelCountText
                text: "0 models"
                color: "#aaaaaa"
                font.pixelSize: 12
            }
        }
        
        // Folder selector
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            
            Text {
                text: "Folder:"
                color: "#888888"
                font.pixelSize: 11
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 32
                color: "#2a2a2a"
                border.color: "#444"
                radius: 4
                
                TextEdit {
                    id: folderPathText
                    anchors.fill: parent
                    anchors.margins: 8
                    color: "#aaaaaa"
                    font.pixelSize: 10
                    readOnly: true
                    verticalAlignment: TextEdit.AlignVCenter
                }
            }
            
            Button {
                text: "Browse"
                onClicked: folderDialog.open()
            }
            
            Button {
                text: "Refresh"
                onClicked: {
                    if (currentFolder) {
                        loadModelsFromFolder(currentFolder)
                    }
                }
            }
        }
        
        // Status message
        Text {
            id: statusText
            Layout.fillWidth: true
            color: "#888888"
            font.pixelSize: 10
            text: "Select a folder to view models"
        }
        
        // Models grid
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            GridView {
                id: modelsGrid
                cellWidth: 250 + 20
                cellHeight: 380 + 20
                model: modelManager
                
                delegate: Item {
                    width: modelsGrid.cellWidth
                    height: modelsGrid.cellHeight
                    
                    ModelCard {
                        anchors.centerIn: parent
                        modelInfo: modelData
                        
                        onClicked: {
                            modelDetailsDialog.show(modelData)
                        }
                        
                        onEditHashClicked: {
                            editHashDialog.show(modelData.path, modelData)
                        }
                        
                        onFetchMetadataClicked: {
                            civitaiUrlDialog.show(modelData)
                        }
                    }
                }
            }
        }
        
        // Footer
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            
            Button {
                text: "Export Metadata"
                onClicked: exportDialog.open()
            }
            
            Button {
                text: "Import Metadata"
                onClicked: importDialog.open()
            }
            
            Item {
                Layout.fillWidth: true
            }
        }
    }
    
    // Folder selection dialog
    FolderDialog {
        id: folderDialog
        onAccepted: {
            folderPathText.text = folder
            loadModelsFromFolder(folder)
        }
    }
    
    // Model details dialog
    Rectangle {
        id: modelDetailsDialog
        
        anchors.centerIn: parent
        width: 600
        height: 500
        color: "#2a2a2a"
        radius: 8
        border.color: "#444"
        visible: false
        z: 1000
        
        property var currentModel: null
        
        function show(model) {
            currentModel = model
            modelDetailsText.text = buildDetailsText(model)
            visible = true
        }
        
        function buildDetailsText(model) {
            var text = "<b>Name:</b> " + model.name + "<br>"
            text += "<b>Path:</b> " + model.path + "<br>"
            text += "<b>Size:</b> " + formatFileSize(model.size) + "<br>"
            text += "<b>Hash:</b> " + (model.hash || "Not set") + "<br>"
            text += "<b>Hash Type:</b> " + (model.hashType || "Unknown") + "<br>"
            
            if (model.civitaiName) {
                text += "<br><b>Civitai Info:</b><br>"
                text += "  Name: " + model.civitaiName + "<br>"
                text += "  Type: " + model.civitaiType + "<br>"
                text += "  ID: " + model.civitaiId + "<br>"
                text += "  Base Model: " + (model.baseModel || "Unknown") + "<br>"
            }
            
            if (model.triggerWords && model.triggerWords.length > 0) {
                text += "<br><b>Trigger Words:</b><br>"
                for (var i = 0; i < model.triggerWords.length; i++) {
                    text += "  • " + model.triggerWords[i] + "<br>"
                }
            }
            
            if (model.description) {
                text += "<br><b>Description:</b><br>"
                text += model.description
            }
            
            return text
        }
        
        function formatFileSize(bytes) {\n            if (bytes === 0) return \"0 Bytes\"\n            var k = 1024\n            var sizes = [\"Bytes\", \"KB\", \"MB\", \"GB\"]\n            var i = Math.floor(Math.log(bytes) / Math.log(k))\n            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + \" \" + sizes[i]\n        }\n        \n        ColumnLayout {\n            anchors.fill: parent\n            anchors.margins: 16\n            spacing: 12\n            \n            Text {\n                text: \"Model Details\"\n                color: \"#ffffff\"\n                font.bold: true\n                font.pixelSize: 16\n            }\n            \n            ScrollView {\n                Layout.fillWidth: true\n                Layout.fillHeight: true\n                \n                TextEdit {\n                    id: modelDetailsText\n                    color: \"#aaaaaa\"\n                    font.pixelSize: 11\n                    readOnly: true\n                    textFormat: TextEdit.RichText\n                    wrapMode: TextEdit.Wrap\n                }\n            }\n            \n            RowLayout {\n                Layout.fillWidth: true\n                spacing: 8\n                \n                Item {\n                    Layout.fillWidth: true\n                }\n                \n                Button {\n                    text: \"Close\"\n                    onClicked: modelDetailsDialog.visible = false\n                }\n            }\n        }\n    }\n    \n    // Edit hash dialog\n    EditHashDialog {\n        id: editHashDialog\n        parent: modelsPanel\n        \n        onHashChanged: {\n            if (modelManager && editHashDialog.modelPath) {\n                modelManager.set_model_hash(editHashDialog.modelPath, hash, hashType)\n            }\n        }\n    }\n    \n    // Civitai URL input dialog\n    Rectangle {\n        id: civitaiUrlDialog\n        \n        anchors.centerIn: parent\n        width: 500\n        height: 250\n        color: \"#2a2a2a\"\n        radius: 8\n        border.color: \"#444\"\n        visible: false\n        z: 1000\n        \n        property var currentModel: null\n        \n        function show(model) {\n            currentModel = model\n            civitaiUrlInput.text = \"\"\n            dialogStatusText.text = \"\"\n            visible = true\n        }\n        \n        ColumnLayout {\n            anchors.fill: parent\n            anchors.margins: 16\n            spacing: 12\n            \n            Text {\n                text: \"Fetch from Civitai\"\n                color: \"#ffffff\"\n                font.bold: true\n                font.pixelSize: 14\n            }\n            \n            Text {\n                Layout.fillWidth: true\n                text: \"Enter Civitai model URL or ID to fetch metadata\"\n                color: \"#888888\"\n                font.pixelSize: 11\n                wrapMode: Text.Wrap\n            }\n            \n            Rectangle {\n                Layout.fillWidth: true\n                height: 40\n                color: \"#1a1a1a\"\n                border.color: \"#444\"\n                radius: 4\n                \n                TextInput {\n                    id: civitaiUrlInput\n                    anchors.fill: parent\n                    anchors.margins: 8\n                    color: \"#aaaaaa\"\n                    font.pixelSize: 11\n                    selectByMouse: true\n                    placeholderText: \"e.g., https://civitai.com/models/123456\"\n                }\n            }\n            \n            Text {\n                id: dialogStatusText\n                Layout.fillWidth: true\n                color: \"#888888\"\n                font.pixelSize: 10\n                wrapMode: Text.Wrap\n            }\n            \n            Item {\n                Layout.fillHeight: true\n            }\n            \n            RowLayout {\n                Layout.fillWidth: true\n                spacing: 8\n                \n                Item {\n                    Layout.fillWidth: true\n                }\n                \n                Button {\n                    text: \"Cancel\"\n                    onClicked: civitaiUrlDialog.visible = false\n                }\n                \n                Button {\n                    text: \"Fetch\"\n                    enabled: civitaiUrlInput.text.trim().length > 0\n                    onClicked: {\n                        if (modelManager && civitaiUrlDialog.currentModel) {\n                            dialogStatusText.text = \"Fetching from Civitai...\"\n                            dialogStatusText.color = \"#ffcc00\"\n                            modelManager.fetch_civitai_metadata(\n                                civitaiUrlDialog.currentModel.path,\n                                civitaiUrlInput.text\n                            )\n                            civitaiUrlDialog.visible = false\n                        }\n                    }\n                }\n            }\n        }\n    }\n    \n    // Export metadata dialog\n    FileDialog {\n        id: exportDialog\n        title: \"Export Metadata\"\n        folder: shortcuts.home\n        selectExisting: false\n        nameFilters: [\"JSON Files (*.json)\"]\n        \n        onAccepted: {\n            if (modelManager) {\n                var result = modelManager.export_all_metadata(fileUrls[0])\n                statusText.text = result\n            }\n        }\n    }\n    \n    // Import metadata dialog\n    FileDialog {\n        id: importDialog\n        title: \"Import Metadata\"\n        folder: shortcuts.home\n        selectExisting: true\n        nameFilters: [\"JSON Files (*.json)\"]\n        \n        onAccepted: {\n            if (modelManager && currentFolder) {\n                var result = modelManager.import_metadata(fileUrls[0], currentFolder)\n                statusText.text = result\n            }\n        }\n    }\n    \n    // Connect to model manager signals\n    Connections {\n        target: modelManager\n        \n        onModelsUpdated: {\n            modelCountText.text = modelManager.modelCount + \" models\"\n            modelsGrid.forceLayout()\n        }\n        \n        onFetchProgress: {\n            statusText.text = message\n            statusText.color = \"#ffcc00\"\n        }\n        \n        onFetchError: {\n            statusText.text = \"Error: \" + message\n            statusText.color = \"#ff6666\"\n        }\n    }\n}\n
