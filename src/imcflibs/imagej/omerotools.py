"""Functions allowing to interact with an OMERO server.

Contains helpers to parse URLs and / or OMERO image IDs, connect to OMERO and
fetch images from the server.

Requires the [`simple-omero-client`][simple-omero-client] JAR to be installed.

[simple-omero-client]: https://github.com/GReD-Clermont/simple-omero-client
"""

from java.lang import Long


from fr.igred.omero import Client
from fr.igred.omero.annotations import MapAnnotationWrapper


def parse_url(client, omero_str):
    """Parse an OMERO URL / image IDs into the respective ImageWrapper objects.

    Assemble a list of ImageWrapper objects from one of the following inputs:

    - An OMERO URL (as retrieved e.g. from OMERO.web).
    - One or more OMERO image IDs.
    - An OMERO Dataset ID.

    Parameters
    ----------
    client : fr.igred.omero.Client
        Client used for login to OMERO.
    omero_str : str
        Either an URL from OMERO or image IDs separated by commas.

    Returns
    -------
    list(fr.igred.omero.repository.ImageWrapper)
        List of ImageWrappers parsed from the string.
    """
    image_ids = []
    dataset_ids = []
    image_wpr_list = []

    # Check if the url is a dataset
    if "dataset-" in omero_str:
        # If there are multiple datasets
        if "|" in omero_str:
            parts = omero_str.split("|")
            for part in parts:
                if "dataset-" in part:
                    image_ids.extend(
                        [
                            image
                            for image in client.getDataset(
                                Long(part.split("dataset-")[1].split("/")[0])
                            ).getImages()
                        ]
                    )
                    dataset_id = Long(part.split("dataset-")[1].split("/")[0])
                    dataset_ids.append(dataset_id)
        else:
            image_ids.extend(
                [
                    image
                    for image in client.getDataset(
                        Long(omero_str.split("dataset-")[1].split("/")[0])
                    ).getImages()
                ]
            )
            # If there is only one dataset
            dataset_id = Long(omero_str.split("dataset-")[1].split("/")[0])
            dataset_ids.append(dataset_id)

        # Get the images from the dataset
        for dataset_id in dataset_ids:
            dataset_wpr = client.getDataset(dataset_id)
            image_wpr_list.extend(dataset_wpr.getImages())

        return image_wpr_list

    # Check if the url is an image
    elif "image-" in omero_str:
        image_ids = omero_str.split("image-")
        image_ids.pop(0)
        image_ids = [s.split("%")[0].replace("|", "") for s in image_ids]
    else:
        image_ids = (
            [s.split("%")[0].replace("|", "") for s in omero_str.split("image-")[1:]]
            if "image-" in omero_str
            else omero_str.split(",")
        )
        # If it is a list of IDs separated by commas
        image_ids = omero_str.split(",")

    return [client.getImage(Long(image_id)) for image_id in image_ids]


def connect(host, port, username, password):
    """Connect to OMERO using the credentials provided.

    Parameters
    ----------
    host : str
        The address (FQDN or IP) of the OMERO server.
    port : int
        The port number for the OMERO server.
    username : str
        The username for authentication.
    password : str
        The password for authentication.

    Returns
    -------
    fr.igred.omero.Client
        A Client object representing the connection to the OMERO server.
    """
    # Create a new OMERO client
    client = Client()

    # Connect to the OMERO server using provided credentials
    client.connect(host, port, username, password)

    # Return the connected client
    return client


def fetch_image(client, image_id):
    """Fetch an image from an OMERO server and open it as an ImagePlus.

    Parameters
    ----------
    client : fr.igred.omero.Client
        The client object used to connect to the OMERO server.
    image_id : int
        The ID of the image to fetch.

    Returns
    -------
    ij.ImagePlus
        The fetched image as an ImagePlus.
    """

    # Fetch the image from the OMERO server
    image_wpr = client.getImage(Long(image_id))

    # Convert the image to an ImagePlus
    return image_wpr.toImagePlus()


def upload_image_to_omero(user_client, path, dataset_id):
    """Upload an image to OMERO.

    Parameters
    ----------
    user_client : fr.igred.omero.Client
        The client object used to connect to the OMERO server.
    path : str
        Path of the file to upload back to OMERO.
    dataset_id : Long
        ID of the dataset where to upload the file.

    Returns
    -------
    Long
        ID of the uploaded image
    """
    return user_client.getDataset(Long(dataset_id)).importImage(user_client, path)[0]


def add_annotation(client, repository_wpr, annotations, header):
    """Add an annotation to an OMERO object.

    Parameters
    ----------
    client : fr.igred.omero.Client
        The client object used to connect to the OMERO server.
    repository_wpr : fr.igred.omero.repositor.GenericRepositoryObjectWrapper
        Wrapper to the object for the anotation.
    annotations : dict
        Dictionary with the annotation to add.
    header : str
        Name for the annotation header.
    """
    # for pair in dict:
    #     result.add
    map_annotation_wpr = MapAnnotationWrapper(annotations)
    map_annotation_wpr.setNameSpace(header)
    repository_wpr.addMapAnnotation(client, map_annotation_wpr)


def find_dataset(client, dataset_id):
    """Retrieve a dataset (wrapper) from the OMERO server.

    Parameters
    ----------
    client : fr.igred.omero.Client
        The client object used to connect to the OMERO server.
    dataset_id : int
        The ID of the dataset to retrieve.

    Returns
    -------
    fr.igred.omero.repositor.DatasetWrapper
        The dataset wrapper retrieved from the server.
    """
    # Fetch the dataset from the OMERO server using the provided dataset ID
    return client.getDataset(Long(dataset_id))
