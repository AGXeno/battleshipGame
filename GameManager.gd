# GameManager.gd
# Handles win/lose conditions and UI in Sea-Ping Warfare
extends Node

@export var ui_label_path := NodePath("CanvasLayer/Label") # Path to your UI label
@export var restart_button_path := NodePath("CanvasLayer/RestartButton") # Path to your restart button

var game_over := false

func _ready():
    # Connect to signals for when enemies or player are destroyed
    get_tree().connect("node_removed", Callable(self, "_on_node_removed"))
    # Hide and connect the restart button
    var button = get_node_or_null(restart_button_path)
    if button:
        button.visible = false
        button.pressed.connect(_on_restart_pressed)

func _on_node_removed(node):
    if game_over:
        return
    if node.is_in_group("enemy"):
        # Check if any enemies remain
        var enemies = get_tree().get_nodes_in_group("enemy")
        if enemies.size() == 0:
            show_message("Victory!")
            game_over = true
    elif node.is_in_group("player"):
        show_message("Game Over")
        game_over = true

func show_message(text):
    var label = get_node(ui_label_path)
    label.text = text
    label.visible = true
    var button = get_node_or_null(restart_button_path)
    if button:
        button.visible = true

func _on_restart_pressed():
    get_tree().reload_current_scene() 