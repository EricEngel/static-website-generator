from textnode import *
from htmlnode import *
import re


def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception(f"Invalid TextType: {text_node}")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    if len(old_nodes) == 0:
        raise Exception("No nodes supplied!")
    
    result = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            result.append(node)
            continue
        items = []
        if node.text.count(delimiter) >= 2 and node.text.count(delimiter) % 2 == 0:
            items = node.text.split(sep=delimiter)
            for i in range(len(items)):
                if i % 2 == 0:
                    result.append( TextNode(items[i], TextType.TEXT) )
                else:
                    result.append( TextNode(items[i], text_type) )
        elif node.text.count(delimiter) == 0:
            result.append(node)
        else:
            raise Exception("Input error: Invalid markdown syntax!")
    return result


def extract_markdown_images(text):
    result = []
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    result = []
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches


def split_nodes_image(old_nodes):
    if len(old_nodes) == 0:
        raise Exception("No nodes supplied!")
    
    result = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            result.append(node)
            continue
        images = extract_markdown_images(node.text)
        current_text = node.text
        for image in images:
            image_alt = image[0]
            image_url = image[1]
            sections = current_text.split(f"![{image_alt}]({image_url})", 1)
            if sections[0]:
                result.append( TextNode(sections[0], TextType.TEXT) )
            result.append( TextNode(image_alt, TextType.IMAGE, image_url) )
            current_text = sections[1]
        if current_text and current_text.strip() != "":
            result.append( TextNode(current_text, TextType.TEXT) )
    return result


def split_nodes_link(old_nodes):
    if len(old_nodes) == 0:
        raise Exception("No nodes supplied!")
    
    result = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            result.append(node)
            continue
        links = extract_markdown_links(node.text)
        current_text = node.text
        for link in links:
            link_text = link[0]
            link_url = link[1]
            sections = current_text.split(f"[{link_text}]({link_url})", 1)
            if sections[0]:
                result.append( TextNode(sections[0], TextType.TEXT) )
            result.append( TextNode(link_text, TextType.LINK, link_url) )
            if len(sections) > 1:
                current_text = sections[1]
        if current_text and current_text.strip() != "":
            result.append( TextNode(current_text, TextType.TEXT) )
    return result


def text_to_textnodes(text):
    node = TextNode(text, TextType.TEXT)
    result = split_nodes_delimiter([node], "**", TextType.BOLD)
    result = split_nodes_delimiter(result, "_", TextType.ITALIC)
    result = split_nodes_delimiter(result, "`", TextType.CODE)
    result = split_nodes_link(result)
    result = split_nodes_image(result)
    return result


def main():
    obj = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(obj)


if __name__ == "__main__":
    main()