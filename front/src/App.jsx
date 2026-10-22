import { useState } from "react";
import "./App.css";
import {StudyMethodTitle, ShowImportMesh, MeshView} from "./components/home";

function App(){
  const [mesh, setMesh] = useState(null);

  return (
    <>
      <StudyMethodTitle/>
      <ShowImportMesh onMeshLoaded={setMesh}/>
      {mesh && <MeshView mesh={mesh}/>}
    </>
  )
}

export default App
