import { useState } from "react";
import "./App.css";
import {StudyMethodTitle, ShowImportMesh, MeshView} from "./components/home";
import { ShowLogin } from "./components/login";

function App(){
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [mesh, setMesh] = useState(null);

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
