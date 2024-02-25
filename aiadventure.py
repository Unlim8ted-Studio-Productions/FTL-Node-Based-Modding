import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from torch.utils.data import Dataset, DataLoader
import xml.etree.ElementTree as ET
from asciitree import Traversal


# Define a dataset class to load and preprocess the XML data
class FTLDataSet(Dataset):
    def __init__(self, file_path, tokenizer):
        self.data = self.load_data(file_path)
        self.tokenizer = tokenizer

    def load_data(self, file_path):
        with open(file_path, "r", encoding="utf8") as file:
            tree = file.read()

        elements_list = self.split_text_by_event_with_name(tree)
        return elements_list[: int(input("number of samples"))]
        # Function to traverse the ElementTree and append elements to the list

    def split_text_by_event_with_name(self, xml_string):
        events = []
        root = ET.fromstring(xml_string)
        current_event = None

        for event in root.findall(".//event[@name]"):
            if current_event is not None:
                events.append(ET.tostring(current_event, encoding="unicode"))
            current_event = event

        if current_event is not None:
            events.append(ET.tostring(current_event, encoding="unicode"))

        return events

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        xml_text = self.data[idx]
        tokenized_text = self.tokenizer(
            xml_text, return_tensors="pt", padding=True, truncation=True
        )
        return tokenized_text


# Function to convert XML tree to ASCII tree
def xml_to_ascii(element, level=0):
    """+ ':'
    Converts XML element to ASCII format.
    Parameters:
        - element (ElementTree.Element): XML element to be converted.
        - level (int): Indentation level, default is 0.
    Returns:
        - generator: ASCII representation of the XML element.
    Processing Logic:
        - Recursively iterates through all child elements.
        - Adds indentation for each level.
        - Handles elements with and without text.
        - Yields each line of the ASCII representation."""
    if len(element):
        yield "+-" + element.tag
        for child in element:
            for line in xml_to_ascii(child, level + 1):
                yield "| " + line
    else:
        if element.text:
            yield "+-" + element.tag + ": " + element.text
        else:
            yield "+-" + element.tag


# Function to convert ASCII tree to XML
def ascii_to_xml(lines, parent=None):
    """Convert ASCII text to XML format.
    Parameters:
        - lines (list): List of ASCII lines to be converted.
        - parent (Element, optional): Parent element to append converted elements to. Defaults to None.
    Returns:
        - parent (Element): Parent element with converted XML elements appended.
    Processing Logic:
        - Strip indentation from each line.
        - Split line into tag and text.
        - Create an Element with the tag.
        - Append text to Element if present.
        - Append Element to parent if parent is not None.
        - Find children elements by comparing indentation.
        - Recursively call function with children elements and current Element as parent.
        - Return parent Element with all converted elements appended."""
    for line in lines:
        indent = len(line) - len(line.lstrip())
        tag_text = line.lstrip().replace("+-", "").strip()
        tag = tag_text.split(":")[0]
        text = tag_text.split(": ")[1] if ": " in tag_text else None
        element = ET.Element(tag)
        if text:
            element.text = text
        if parent is not None:
            parent.append(element)
        children = []
        for next_line in lines:
            next_indent = len(next_line) - len(next_line.lstrip())
            if next_indent == indent + 2:
                children.append(next_line)
            elif next_indent <= indent:
                break
        if children:
            ascii_to_xml(children, parent=element)
    return parent


# Define collate function for DataLoader
def collate_tensor_fn(batch, device):
    """Collates a batch of input tensors and returns them in a dictionary.
    Parameters:
        - batch (list): A list of dictionaries containing input tensors.
        - device (torch.device): The device to move the tensors to.
    Returns:
        - dict: A dictionary containing the collated input tensors.
    Processing Logic:
        - Get the maximum length of the input tensors in the batch.
        - Pad the input tensors with zeros to match the maximum length.
        - Move the tensors to the specified device.
        - Return the collated tensors in a dictionary."""
    max_len = max(len(entry["input_ids"][0]) for entry in batch)
    input_ids = [
        entry["input_ids"][0].tolist() + [0] * (max_len - len(entry["input_ids"][0]))
        for entry in batch
    ]
    attention_mask = [
        entry["attention_mask"][0].tolist()
        + [0] * (max_len - len(entry["attention_mask"][0]))
        for entry in batch
    ]
    # Move tensors to the correct device
    input_ids = torch.tensor(input_ids, device=device)
    attention_mask = torch.tensor(attention_mask, device=device)
    return {"input_ids": input_ids, "attention_mask": attention_mask}


# Define the training function
def train_model(
    dataset,
    model: GPT2LMHeadModel,
    tokenizer,
    num_epochs=3,
    batch_size=16,
    learning_rate=2e-5,
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
):
    # Define DataLoader with custom collate function
    """Train a model on a given dataset.
    Parameters:
        - dataset (torch.utils.data.Dataset): Dataset to train the model on.
        - model (transformers.PreTrainedModel): Pre-trained model to be trained.
        - tokenizer (transformers.PreTrainedTokenizer): Tokenizer used to tokenize the dataset.
        - num_epochs (int): Number of epochs to train the model for. Default is 3.
        - batch_size (int): Batch size for the DataLoader. Default is 16.
        - learning_rate (float): Learning rate for the optimizer. Default is 2e-5.
        - device (torch.device): Device to use for training. Default is "cuda" if available, else "cpu".
    Returns:
        - None: The trained model is saved to disk.
    Processing Logic:
        - Uses a custom collate function for the DataLoader.
        - Uses AdamW optimizer.
        - Prints average loss for each epoch.
        - Saves the trained model to disk."""

    with tqdm(desc="Creating data loader", total=100) as pbar:
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            collate_fn=lambda batch: collate_tensor_fn(batch, device),
        )
        pbar.update(100)

    # Define optimizer
    with tqdm(desc="Define optimizer", total=100) as pbar:
        optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
        pbar.update(100)

    # Training loop
    with tqdm(
        iterable=num_epochs, desc="Training", total=num_epochs, unit="epochs"
    ) as pbar:
        for epoch in range(num_epochs):
            model.train()
            total_loss = 0
            for batch in dataloader:
                # Move batch to device
                batch = {k: v.to(device) for k, v in batch.items()}

                # Forward pass
                outputs = model(**batch, labels=batch["input_ids"])

                # Compute loss
                loss = outputs.loss

                # Backward pass
                loss.backward()

                # Update weights
                optimizer.step()
                optimizer.zero_grad()

                total_loss += loss.item()

            # Print average loss for the epoch
            print(f"Epoch {epoch+1}, Average Loss: {total_loss/len(dataloader)}")
            pbar.update(epoch + 1)

    # Save the trained model
    model.save_pretrained("trained_model")


from tqdm import tqdm  # Import tqdm for the loading bar


def generate_text(prompt, tokenizer, model, max_length=1000):
    """Generates text based on a given prompt.
    Parameters:
        - prompt (str): The text prompt to generate from.
        - tokenizer (obj): A tokenizer object used to encode the prompt.
        - model (obj): A model object used to generate the text.
        - max_length (int): The maximum length of the generated text. Default is 100.
    Returns:
        - generated_text (str): The generated text based on the given prompt.
    Processing Logic:
        - Encodes the prompt using the tokenizer.
        - Generates text using the model.
        - Decodes the generated text and removes any special tokens."""
    print("Encoding the prompt...")
    input_ids = tokenizer.encode(prompt, return_tensors="pt")

    print("Generating text...")
    with tqdm(total=max_length, desc="Generating Text", unit="tokens") as pbar:
        output = model.generate(
            input_ids, max_length=max_length, num_return_sequences=1
        )
        pbar.update(len(output[0]))

    print("Decoding and post-processing the generated text...")
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    print("Text generation completed.")
    return generated_text


def main():
    """This function is used to generate text using a pre-trained GPT-2 model.
    It takes in a prompt, tokenizer, and model as parameters and returns the generated text.
    The function first loads and preprocesses the dataset, then trains the model using the dataset.
    Once trained, the function loads the trained model and uses it to generate text based on the given prompt.
    The generated text is then printed."""

    # Define the model and tokenizer
    device = torch.device("cpu")  # ("cuda" if torch.cuda.is_available() else "cpu")
    model_name = "gpt2-medium"

    with tqdm(desc="Loading tokenizer", total=100) as pbar:
        tokenizer = GPT2Tokenizer.from_pretrained(model_name, device=device)
        pbar.update(100)

    if input("Train the model? Enter anything but nothing to proceed: "):
        # Set padding token to eos_token
        tokenizer.pad_token = tokenizer.eos_token
        with tqdm(desc="Loading model and pushing to device", total=100) as pbar:
            model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
            pbar.update(100)

        dataset = FTLDataSet("AIdata\\ftl_data.xml", tokenizer)

        # Wrap dataset loading with tqdm
        with tqdm(total=len(dataset), desc="Training model") as pbar:
            train_model(dataset, model, tokenizer, device=device)
            pbar.update(len(dataset))

    print("Loading the trained model...")
    # Wrap model loading with tqdm
    with tqdm(desc="Loading trained model", total=100) as pbar:
        model = GPT2LMHeadModel.from_pretrained("trained_model").to(device)
        pbar.update(100)

    prompt = "Upon arriving at this beacon"
    print("Generating text based on the prompt...")
    generated_text = generate_text(prompt, tokenizer, model)
    print("Generated Text:", generated_text)


if __name__ == "__main__":
    main()
