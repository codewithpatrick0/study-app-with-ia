import { useEffect, useState } from "react";
import "./App.css";
import { StudyMethodTitle, ShowImportMesh, MeshView } from "./components/home";
import { ShowLogin } from "./components/login";

function App(){
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [checkingSession, setCheckingSession] = useState(true);
  const [mesh, setMesh] = useState(null);

  // On page load, ask the backend if the auth cookie is still valid
  useEffect(() => {
    async function checkSession() {
      try {
        const response = await fetch("http://localhost:8000/auth/me", {
          credentials: "include", // Send the auth cookie
        });

        if (response.ok) {
          setIsAuthorized(true);
        }
      } catch (err) {
        console.error("error:", err);
      } finally {
        setCheckingSession(false);
      }
    }

    checkSession();
  }, []);

  if (checkingSession) {
    return (
      <div className="session-check" role="status">
        <span className="spinner" aria-hidden="true"></span>
        <p>Checking login status...</p>
      </div>
    );
  }

  return isAuthorized ? (
    <>
      <StudyMethodTitle />
      <ShowImportMesh onMeshLoaded={setMesh} />
      {mesh && <MeshView mesh={mesh} />}
    </>
  ) : (
    <>
      <ShowLogin onLogin={() => setIsAuthorized(true)} />
    </>
  )
}

export default App
