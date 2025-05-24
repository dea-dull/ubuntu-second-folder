import os
import logging
from typing import List
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from embeddings_processor import generate_image_embedding
from pinecone_integrator import upload_embeddings

# Constants for configuration
MAX_RETRIES = 3
BATCH_SIZE = 100
UPLOAD_TIMEOUT = 120  # Timeout for batch uploads in seconds


def generate_embeddings(image_streams: List[bytes], organisation_id: str, timeout: int = 60) -> List[dict]:
    """
    Generates embeddings for a list of image byte streams concurrently.

    Args:
        image_streams (List[bytes]): List of image byte streams.  --  The image_streams list is like a queue of incoming packages.
        organisation_id (str): Unique identifier for the organisation. -- the company name stamped on every label for identification.
        timeout (int): Timeout in seconds for each embedding generation task.

    Returns:
        List[dict]: A list of embeddings with associated metadata.

    """
    if not image_streams:
        logging.warning("No images provided for processing.")
        return []

    metadata_template = {
        "organisation_id": organisation_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    with ThreadPoolExecutor() as executor:
        futures = []
        for index, image_data in enumerate(image_streams):
            metadata = {**metadata_template, "file_name": f"image_{index}.jpg"}
            logging.info(f"Submitting task for image {index + 1} with metadata: {metadata}")
            futures.append(executor.submit(generate_image_embedding, image_data, metadata))

        results = []
        for index, future in enumerate(futures):
            for attempt in range(MAX_RETRIES):
                try:
                    result = future.result(timeout=timeout)
                    if result:
                        results.append(result)
                        logging.info(f"Successfully generated embedding for image {index + 1}.")
                    break  # Exit retry loop on success
                except TimeoutError:
                    logging.warning(
                        f"Timeout for image {index + 1}. Retry {attempt + 1}/{MAX_RETRIES}."
                    )
                except Exception as e:
                    logging.error(f"Error processing image {index + 1}: {e}")
                    break  # Exit retry loop on failure

    if not results:
        logging.warning("No embeddings were generated.")
    return results


def upload_embeddings_in_batches(embeddings: List[Dict[str, Any]], index_name : str = None, 
                                  batch_size: int = 100, max_retries: int = 5, upload_timeout: int = 120) -> None:
    """
    Uploads embeddings to Pinecone in batches, with retry logic and timeout.

    Args:
        embeddings (List[dict]): List of embeddings to upload.
        index_name (str): Pinecone index name.
        batch_size (int): Number of embeddings to upload per batch.
        max_retries (int): Maximum retry attempts for a failed batch upload.
        upload_timeout (int): Timeout for each batch upload in seconds.

    Returns:
        None
    """
    if index_name is None:
        index_name = os.getenv("PINECONE_INDEX_NAME", "default_index_name") 


    if not embeddings:
        logging.warning("No embeddings to upload.")
        return

    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(0, len(embeddings), batch_size):
            batch = embeddings[i:i + batch_size]
            logging.info(f"Scheduling batch {i // batch_size + 1} with {len(batch)} embeddings for upload.")
            futures.append(executor.submit(upload_embeddings, batch, index_name))

        for future in futures:
            for attempt in range(max_retries):
                try:
                    future.result(timeout=upload_timeout)
                    logging.info("Batch uploaded successfully.")
                    break
                except TimeoutError:
                    logging.warning(f"Timeout while uploading batch. Retry {attempt + 1}/{max_retries}.")
                except Exception as e:
                    logging.error(f"Error uploading batch: {e}")
                    break

def process_images_concurrently(image_streams: List[bytes], organisation_id: str, 
                                 index_name: str = None, batch_size: int = 100, max_retries: int = 5, 
                                 upload_timeout: int = 60, timeout: int = 60) -> None:
    """
    Main function to process a list of image byte streams concurrently.
    Generates embeddings for each image and uploads them to Pinecone in batches.

    Args:
        image_streams (List[bytes]): List of byte streams representing images.
        organisation_id (str): Unique identifier for the organisation.
        index_name (str): The Pinecone index name.
        batch_size (int): Number of embeddings to upload per batch.
        max_retries (int): Maximum number of retry attempts for batch uploads.
        upload_timeout (int): Timeout in seconds for each batch upload.
        timeout (int): Timeout for each embedding generation task.

    Returns:
        None
    """

    if index_name is None:
        index_name = os.getenv("PINECONE_INDEX_NAME", "default_index_name") 


    if not organisation_id:
        logging.error("Organisation ID is required.")
        return

    logging.info(f"Starting image processing for organisation {organisation_id}.")

    # Generate embeddings (this is assumed to be a function that creates embeddings from the image streams)
    embeddings = generate_embeddings(image_streams, organisation_id, timeout)

    # Upload embeddings in batches
    upload_embeddings_in_batches(embeddings, index_name, batch_size, max_retries, upload_timeout)

    logging.info(f"Image processing completed for organisation {organisation_id}.")
