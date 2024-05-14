import cv2
import numpy as np

# Load ESPCN model
espcn_model = cv2.dnn.readNetFromTensorflow("ESPCN_x4.pb")

def increase_resolution(frame):
    # Convert frame to float32
    frame_float32 = frame.astype(np.float32) / 255.0

    # Preprocess frame for ESPCN model
    blob = cv2.dnn.blobFromImage(frame_float32, scalefactor=1.0, size=(48, 48), mean=(0, 0, 0), swapRB=False, crop=False)

    # Set input to ESPCN model and perform inference
    espcn_model.setInput(blob)
    output = espcn_model.forward()

    # Rescale output to [0, 255]
    output *= 255.0
    output = np.clip(output, 0, 255)
    output = output.astype(np.uint8)

    # Convert back to BGR format
    output_bgr = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)

    return output_bgr

# Function to process and crop video
def process_and_crop_video(input_path, output_path):
    # Open input video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open input video.")
        return

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create VideoWriter for output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Read and process each frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Crop frame (insert your crop logic here)
        cropped_frame = frame  # Replace with actual crop logic

        # Increase resolution of cropped frame using ESPCN
        high_res_frame = increase_resolution(cropped_frame)

        # Write high resolution frame to output video
        out.write(high_res_frame)

    # Release resources
    cap.release()
    out.release()

    print("Video processing and cropping completed!")

if __name__ == "__main__":
    input_video_path = "input_video.mp4"  # Path to input video
    output_video_path = "output_processed_video.mp4"  # Path to save processed video
    process_and_crop_video(input_video_path, output_video_path)
