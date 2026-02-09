import { useEffect, useState } from "react";
import { uploadImage, getJobs } from "./api";
import "./App.css";

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load jobs
  async function loadJobs() {
    try {
      const data = await getJobs();
      setJobs(data);
    } catch {
      setError("Please login again");
    }
  }

  useEffect(() => {
    loadJobs();
  }, []);

  // Upload
  async function handleUpload() {
    if (!file) return;

    try {
      setLoading(true);
      await uploadImage(file);
      await loadJobs();
      setFile(null);
    } catch {
      alert("Upload failed");
    }

    setLoading(false);
  }

  return (
    <div className="dashboard">

      <h1>📊 AI Image Dashboard</h1>

      {/* Upload Box */}
      <div className="upload-box">

        <input
          type="file"
          accept="image/png,image/jpeg"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Uploading..." : "Upload Image"}
        </button>

      </div>

      {error && <p className="error">{error}</p>}

      {/* Jobs List */}
      <h2>Your Jobs</h2>

      {jobs.length === 0 && (
        <p>No jobs yet. Upload an image.</p>
      )}

      <div className="jobs">

        {jobs.map((job) => (
          <div key={job.id} className="job-card">

            <p><b>Job ID:</b> {job.id}</p>
            <p><b>Status:</b> {job.status}</p>

            {/* Original Image */}
            {job.original_url && (
              <>
                <p>Original</p>
                <img src={job.original_url} />
              </>
            )}

            {/* Output Image */}
            {job.output_url && (
              <>
                <p>Detected</p>
                <img src={job.output_url} />
              </>
            )}

            {/* CSV */}
            {job.csv_url && (
              <a href={job.csv_url} download>
                ⬇ Download CSV
              </a>
            )}

          </div>
        ))}

      </div>

    </div>
  );
}
