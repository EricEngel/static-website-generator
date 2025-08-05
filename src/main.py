from textnode import *
from htmlnode import *
from enum import Enum
import os, sys, shutil, re

BlockType = Enum('BlockType', ['PARAGRAPH', 'HEADING', 'CODE', 'QUOTE', 'UNORDERED_LIST', 'ORDERED_LIST'])


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


def markdown_to_blocks(markdown):
    blocks = markdown.split('\n\n')
    new_blocks = []
    for i in range(len(blocks)):
        item = blocks[i].strip()
        if len(blocks[i]) != 0:
            new_blocks.append(item)
    return new_blocks


def block_to_block_type(block):
    lines = block.split('\n')

    if lines[0][:1] == '#':
        return BlockType.HEADING
    elif lines[0][:3] == "```" and lines[len(lines) - 1][-3:] == "```":
        return BlockType.CODE
    elif lines[0][:1] == '>':
        valid_quote = True
        for line in lines:
            if line[:1] != ">":
                valid_quote = False
        if valid_quote:
            return BlockType.QUOTE
    elif lines[0][:2] == '- ':
        valid_unordered = True
        for line in lines:
            if line[:2] != "- ":
                valid_unordered = False
        if valid_unordered:
            return BlockType.UNORDERED_LIST
    elif lines[0][:1] >= '0' and lines[0][:1] <= '9':
        valid_ordered = True
        for line in lines:
            if line[:1] < '0' and line[:1] > '9' and line[1:1] != ".":
                valid_unordered = False
        if valid_ordered:
            return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH


def text_to_children(text):
    nodes = text_to_textnodes(text)
    children = []
    for node in nodes:
        children.append(text_node_to_html_node(node))
    return children


def remove_symbols_from_block(block):
    new_block = ""
    lines = block.split('\n')
    for line in lines:
        if line[:6] == "######":
            line = line[6:].strip()
        elif line[:5] == "#####":
            line = line[5:].strip()
        elif line[:4] == "####":
            line = line[4:].strip()
        elif line[:3] == "###":
            line = line[3:].strip()
        elif line[:2] == "##":
            line = line[2:].strip()
        elif line[:1] == "#":
            line = line[1:].strip()
        elif line[:1] == ">":
            line = line[1:].strip()
        new_block += f"{line}\n"
    return new_block


def add_li_to_block(block):
    new_block = ""
    lines = block.split('\n')
    for line in lines:
        if line[:1] == "-":
            line = line[1:].strip()
        else:
            line = line.split('.', 1)[1].strip()
        new_block += f"<li>{line}</li>\n"
    return new_block


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.PARAGRAPH:
                nodes.append( ParentNode("p", text_to_children(block.replace('\n', ' '))) )
            case BlockType.HEADING:
                if block[:6] == "######":
                    nodes.append( ParentNode("h6", text_to_children(remove_symbols_from_block(block))) )
                elif block[:5] == "#####":
                    nodes.append( ParentNode("h5", text_to_children(remove_symbols_from_block(block))) )
                elif block[:4] == "####":
                    nodes.append( ParentNode("h4", text_to_children(remove_symbols_from_block(block))) )
                elif block[:3] == "###":
                    nodes.append( ParentNode("h3", text_to_children(remove_symbols_from_block(block))) )
                elif block[:2] == "##":
                    nodes.append( ParentNode("h2", text_to_children(remove_symbols_from_block(block))) )
                else:
                    nodes.append( ParentNode("h1", text_to_children(remove_symbols_from_block(block))) )
            case BlockType.CODE:
                nodes.append( ParentNode("pre", [text_node_to_html_node(TextNode(block[4:-3], TextType.CODE))]) )
            case BlockType.QUOTE:
                nodes.append( ParentNode("blockquote", text_to_children(remove_symbols_from_block(block))) )
            case BlockType.UNORDERED_LIST:
                nodes.append( ParentNode("ul", text_to_children(add_li_to_block(block))) )
            case BlockType.ORDERED_LIST:
                nodes.append( ParentNode("ol", text_to_children(add_li_to_block(block))) )
    parent = ParentNode("div", nodes)
    return parent


def extract_title(markdown):
    lines = markdown.split('\n')
    for line in lines:
        if line[:1] == "#" and line[:2] != "##":
            return line[2:].strip()
    raise Exception("Markdown error: h1 header missing.")


def copy_directory(source, destination):
    if os.path.exists(destination):
        shutil.rmtree(destination)
        print(f"Deleted existing directory: {destination}")
    os.mkdir(destination)
    print(f"Created directory: {destination}")

    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        destination_path = os.path.join(destination, item)
        if os.path.isfile(source_path):
            shutil.copy(source_path, destination_path)
            print(f"Copied file: {source_path} to {destination_path}")
        elif os.path.isdir(source_path):
            copy_directory(source_path, destination_path)



def generate_page(site_path, from_path, destination_path, template_path):
    if not os.path.exists(from_path):
        raise Exception("Input file missing!")
    if os.path.exists(destination_path):
        raise Exception("Destination file already exists!")
    if not os.path.exists(template_path):
        raise Exception("Template file missing!")
    
    print(f"Generating page from {from_path} to {destination_path} using {template_path}.")

    # Read the from_path file contents
    md = ""
    f = open(from_path, mode='r')
    md = f.read()
    f.close()

    # Read the template_path file contents
    template = ""
    f = open(template_path, mode='r')
    template = f.read()
    f.close()

    # Retrieve relevant data to be inserted into template
    title = extract_title(md)
    html = markdown_to_html_node(md).to_html()

    # Insert data into template
    final = template.replace("{{ Title }}", title, 1).replace("{{ Content }}", html, 1).replace('href="/', f'href="{site_path}').replace('src="/', f'src="{site_path}')

    # Ensure directory structure exists for destination_path
    if not os.path.exists(os.path.dirname(destination_path)):
        os.makedirs(os.path.dirname(destination_path))

    # Write the new HTML file at destination_path
    f = open(destination_path, mode='w')
    f.write(final)
    f.close()

def generate_pages_recursive(site_path, content_path, destination_path, template_path):
    # Recursively generate pages
    for root, dirs, files in os.walk(content_path):
        for file in files:
            if file.endswith(".md"):
                from_path = os.path.join(root, file)
                
                # Construct destination path
                relative_path = os.path.relpath(from_path, content_path)
                # Correctly join destination_path with the relative directory
                destination_dir = os.path.join(destination_path, os.path.dirname(relative_path)) 
                destination_file = os.path.splitext(os.path.basename(relative_path))[0] + ".html"
                # Use a new variable for the full destination path to avoid overwriting the loop variable
                full_destination_path = os.path.join(destination_dir, destination_file)

                # Pass the correctly constructed full_destination_path
                generate_page(site_path, from_path, full_destination_path, template_path)

def main():
    # Command line arguments. Show help, if requested. Otherwise, set the basepath.
    if sys.argv.__len__() == 2:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Usage: python3 main.py <site_root>")
            sys.exit(1)
        else:
            basepath = sys.argv[1]
            if basepath[-1:] != "/":
                basepath = basepath + "/"
    else:
        basepath = "/"

    copy_directory("./static/", "./docs/")
    generate_pages_recursive(basepath, "./content/", "./docs/", "./template.html")

if __name__ == "__main__":
    main()