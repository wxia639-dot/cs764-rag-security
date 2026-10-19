import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve('.'),skill='C:/Users/惠普/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(root,'work/build/revised_candidate.pptx'),finalPath:path.join(root,'outputs/CS764_RAG_Security_Presentation_Revised.pptx'),pythonExecutable:'C:/Users/惠普/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(root,'work/build/presentation.revised.v2.validation.json')});
console.log(JSON.stringify(result));

