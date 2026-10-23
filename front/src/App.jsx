import { useEffect, useState } from "react";
import "./App.css";
import { StudyMethodTitle, ShowImportMesh, MeshView } from "./components/home";
import { ShowLogin } from "./components/login";
import { ShowRegister } from "./components/register";

function App(){
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [checkingSession, setCheckingSession] = useState(true);
  const [authScreen, setAuthScreen] = useState("login"); // "login" | "register"
  const [notice, setNotice] = useState(null);
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

  if (!isAuthorized) {
    return (
      <main className="auth-page">
        <StudyMethodTitle />

        {authScreen === "register" ? (
          <ShowRegister
            onRegistered={() => {
              setNotice("Account created. You can log in now.");
              setAuthScreen("login");
            }}
            onGoToLogin={() => setAuthScreen("login")}
          />
        ) : (
          <ShowLogin
            notice={notice}
            onLogin={() => setIsAuthorized(true)}
            onGoToRegister={() => {
              setNotice(null);
              setAuthScreen("register");
            }}
          />
        )}
      </main>
    );
  }

  return (
    <>
      <StudyMethodTitle />
      <ShowImportMesh onMeshLoaded={setMesh} />
      {mesh && <MeshView mesh={mesh} />}
    </>
  )
}

export default App
