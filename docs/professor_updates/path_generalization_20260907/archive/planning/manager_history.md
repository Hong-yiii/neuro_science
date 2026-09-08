# Manager state — active full research request (2026-09-07)

User: work in NEW worktree; full hypothesis/ablation/data-handling/research program until concrete defensible research direction; run tests/numbers/graphs and deliver teaching-first professor HTML. Run-to-completion, not just plan. Negative results acceptable; no forced significance.

## Workspace / immutable inputs
- NEW worktree `/home/hongyi-home-lab/neuro_science-path-diagnosis`, branch `research/path-generalization-20260907`, base HEAD `a9d8dac`.
- Original `/home/hongyi-home-lab/neuro_science` has preexisting modified `scripts/place195_graph_path_baseline.py`; preserve. Another `/home/hongyi-home-lab/neuro_science-start-goal-cebra` worktree exists; not ours.
- Runtime `/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python`: torch2.12.0+cu130, CEBRA0.6.1, sklearn1.7.2, NumPy2.3.4. RTX2070 8GB idle at start; ~9.8GB available RAM,308GB free. Do not install/update environments.
- Accepted legacy root R=`/home/hongyi-home-lab/neuro_science/outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906`.
- Primary saved NPZ `R/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz`:104masked source rows,29cells,10bins,82train/22validation,7sessions. Source hash688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567.
- Relaxed40:146sources114train32val/11sessions. Strict6:11sources6train5val/1session. All saved 50/100/200ms tensors exist.
- Original heldout permanently exposed during earlyV6; NEVER evaluate newmodels ontest. Development resplits aren't pristine. Wider extraction ONLY through SplitFilteredAccess before parsing response values; explicitly disclose mixed-file streaming/skipping, not 'physical no testfileaccess'. No supplements beyond195.
- New outputs only newworktree `outputs/path-generalization-20260907`; no symlinking whole oldoutputs or edits to old artifacts.

## Frozen program
Read full `docs/reports/path-generalization-prefit-20260907.md` in newtree (writer is amending precise prefit clarifications). No biological fits/export authorized YET: parent requires implementation/code/data review. User already authorized program overall; this is a parent safety gate. CLI token `--authorized-phase reviewed-code-data-gate` required for all real execution.
A: exact class-balanced empirical-Q validation24absent+6present combos; legacy24model/head replay; exact wholecue product moments and pooled(class,time)cell PCA; exact standardized ridge; MonteCarlo rows16/64/256/1024×20assemblyseeds withrawtotal,binned,PCA3/8/16/29, bothlegacyC1 andC=64/rows; matched finite-sample ridge lambda1 versusexact ridge; source/session contributions/LOO andrelaxed40 real-session source budget. KnownGaussian controls100simulationseeds, trainN3/10/30,valN1/5/20,effect0/.5,analytictrueBA/AUC vsfinite-Q scores; expectedspuriousbetweenclasscovtrace=sum_j sigma_j²(1/n0_s+1/n1_s)/4.
B: native raw→CEBRA,noPCA. hidden32,batch256,temp1,lr3e-4. dim8 rows64 updates1000 Time/Behavior with5assembly×5optimizerseeds=50fits. d3/16/29A0O0=6extra, rows256/1024A0O0d8=4extra,5000stepsA0O0d8=2extra:62observed. Matched14-configfamily(A0O0 only)×20source-labelpermutations=280nullfits; exact permuted-Qvalidation, familymaxBAp; crossedseedgriddiagnosticnotcoveredby narrowerfamilyp. Full losses/checkpoints/predictions/source exposure. Save1000checkpointinside5000andcompare prefix. EstimatedGPUhour-scale~60–90min.
C: broader all195, real per-unit source-linked classifier, no populationstitching. UPDATED prefit amendment: THREE targets: originalMIDDLE, originalANYWHERE sensitivity, and behavior-selected supported_middle for D_N_C_M__N_C_B. See new target-selection section below. Training-onlysession/endpointeligibility≥3sources/class; perunit≥20trainsources. Baselinefullendpointintercepts(unpenalized)+trialindex+duration; augmentlog1p(count/exposure). TRAIN endpoint-demean continuousfeatures thenstandardize residuals soL2defineswithinendpointvariation. λ1 average logisticloss; per-unit→sessionequalaggregate heldoutΔlogloss. 100coherentjoint(mid,any,supported_middle)source-labelshuffles session/E/split and100coarsetemporal-halfnulls, bothmodelsrefit; matchedTHREE-targetmaxstatp, immovable strata reported. Cohorts maydiffer, no targetwinnerhunting. Source counts/exposure join masks/QC etc rigorously audited.

## NEW IMPORTANT finding already told user
Old target is ORDINAL-MIDDLE occurrence, NOT edge-anywherepresence. Code finalize_trial usescorridor_runs[1:-1]. Acceptedcode isconsistent; earlier assistant 'absent=edgeavoided' shorthand waswrong.
From660fixed4->3development paths:
- train393middlepresent;153absent=112neveredge+41edgeoutside-middle.
- val82middlepresent;32absent=22neveredge+10edgeoutside-middle.
- total475middlepresent,134neveredge,51outside-middle.
- ALL51outside-middle paths have2corridor tokens; all660haveemptyV6qc_flags. Notprooftruncation/clockbug.
Dominantmiddlepositive459/475 route CT→RT→RM→RB. Dominantabsent99 RT→CT→CM→RM→RB;50 CT→RT→RM.
Primary104 source subset: trainoldabs30=24never+6outside;valoldabs12=10never+2outside(20180810oneof3abs,20181022oneof2abs).
Anywhere trainnegative counts perprimarysession=[5,2,3,2,5,4,3], soold3/classfloor fails2sessionsafterrelabel; do notsilentlyrelabelprimarybenchmark. KeepTrackA/B originalmiddle; TrackCpairedtargetauditnew estimandsseparatecohorts.
Whitelistscope: union cell_ids fromR/v6-reset-graph-support-audit/v6c_population_membership/selected_component_source_membership.csv is195cells/58sessions. Sortedlist JSON separators(',',':') SHA2924d60f9a52ad7c02e802c28e84a85c6267da023267ac1b507b957e0587f60d. Canenforce195scopewithoutmixed importer metadata.

## Delegation / CURRENT active worker
- Planningfanout2ff20cab completed; outputs `work/research-planning/{design-review,primary-literature,artifact-feasibility}.md`.
- Sole implementation writer initial5abb1497 completed phase1(code/synthetictests/schema/behavioraudit). Created `scripts/place195_path_generalization_phase1.py` (~3077L atreview), `scripts/test_place195_path_generalization_phase1.py`17tests. SyntheticCEBRAsmoke prefix/reload0,7SYNTHETICplots. No biologicalfits/export.
- Phase1handoff `work/research-planning/implementation-phase1.md`.
- Preflightreview46de020f completed: requested explicitexecutiongate +PCA29equivalencecaveat; writerfixedprotocol. Protocolhashthen27f8181586dae1093441bbcc9dd7eb0b7117a4c799d1b72af3a000f9597290e9 (nowmayamend).
- CODEreviewfanoutf39f8053 completed, outputs `work/research-planning/code-review-ab.md`, `code-review-c.md`. Both BLOCKED execution, essential wrappersmissing despite17tests.
- Writer revived/current **76f17d7b** (same session) fixingallreviewfindings. SOLE WRITER; parent shouldnoteditcode/worktreedocs concurrently. Code/data gate STILL CLOSED. Need await phasefixhandoff, personallyreadcriticalseams +independentre-review before launch.
- Worker session `/home/hongyi-home-lab/.pi/agent/sessions/--home-hongyi-home-lab--/2026-09-07T02-06-33-989Z_01a0799e-0405-752d-a4b0-703d16fa17ae/2e7c187d/run-0/session.jsonl`.
- Autoattention60sidlenotice occurred; status showedactivelyworkinglast2s. No actualblock, do notinterruptjustfornotices.

## Critical code-review fixes sent toworker
Review snapshotcodeSHA91954431d4cbbd94179ddb2b0907a6f0da7107ab8eb3994438ad06cc66e591c0, testSHAe77f3068170127b33cbdc150399c02e85cad85a84dbf7a7ec9fd9eadfa45a8fb.
1. TrackA runneronly3ridge rows thenclaimedcomplete; implementallactualstages orhonestlyincomplete.
2. Bnullflagonlyran14UNPERMUTEDconfigs once(no shuffledlabels), not20×14! Musttrulypermute/reassemble/refit/aggregate.
3. Bvalidationwasrandompseudo rows varyingwithrows/A—notexactbalanced-Q. Fixweights/logloss/Brier/predictions.
4. Save1000checkpointin5000runs +checkactualpairedprefix.
5. Cnull default0, temporalhalfhelperunused,no pvalues. Implementboth100nullfamilies2targetmax.
6. Resumeonlyspec hash unsafe. Code/protocol/fullinputs/source/label/array/manifest/configfingerprints andartifact completeness required. No silentreuse/clobber partials; preservefailedattempts.
7. Cexportno195cellallowlist, incompletehash/QC/missingjoins. Enforceacceptedcellwhitelistbeforeparse; poisonunselectedcelltest.
8. UniqueSOURCE eligibility, notrowcounts; localduplicate/inconsistentIDguardsatmodelentry.
9. Parent extras: rejectfractionalcounts beforeint; split/session/cell-sessionjoinasserts; missingrequestedtargetlabels MUSTNOTfallbacktomiddle;zero-validation skipbeforeemptyarraybroadcast;nonconvergedfitsfailclosed; saveobservedperunitparams/scalers/sourceIDs/predictions.
10. TrackC endpoint-demeancontinuousfeaturesBEFOREtrainresidualscaling; testaddingcontextconstants preservespredictions.
11. Genericridgehelperrawunits: callerprimarymuststandardizeusingTRAIN-Qmoments, mapweights/interceptbackforrawscoreconvolution.
12. +/-1ridgeprobabilitynaturalmapclip((score+1)/2), notunexplainedsigmoid; otherwiseonlyBA/AUC/margins, don'tletarbitrarylinkwinpropermetrics.
13. Addmatchedfinite-sampleridgearm(lambda1) versusexactridge; logisticandridgeobjectivesdiffer, cannotcalllogisticconvergingtoridge.
14. Realend-toendsyntheticrunnerchecks(casecounts,realshuffles,exactweights), notonlyutilities. Sevenphase1plots areSYNTHETIC ONLY, notactualresearchfigures.
15. AvoidwrappingeveryfailfastfileparsecalltosilenceauxASTlint; integrityfailures shouldpropagate. Broadauxwarningsaren'tallrealerrors. LSPphase1wasinconclusive/timeouts; ruff/compile/tests passed.
16. FullPCA29 retainscoordinatesbutheadstandardizationchangesregularization; usematchedno-extra-head-rescalingrotationtest. NativeCEBRA29stillhiddenbottleneck16, nonlinearL2norm, notno-compressioncontrol. NOextraarchitecturegridrequested.
17. Workerrecentlookupnpzfiles[] pathwrong: oldcoefs ARE R/final.../v8b/coefs/seed0_raw_total_C1.npz etc. LegacyPCAfirststage mayneedtrain-only reconstruction; distinguishrefitvsreplay, verifysavedpredictions.

## Parent personally read/verified
- Whole project guidelines/canonicalquestion/contract/newaudit/data-volume docs.
- OldV7assemble/loaders,bins,masks;oldV9model/sampler/fitting;SplitFilteredAccessentirebody.
- Currentnewprogramrun_track_a/b/c, run_one_cebra_fit,export,GLM/peruniteligibility/two-targetnull andfreeze_config bodies fromreviewrevision. Need reread fixes.
- Exactold12CEBRAs alltrainBA1.0; Time3seed2valBA/AUC0;Time3seed1valBA.5/AUC.946predallabsent;Time8seed1BA.484/AUC.720.
- Nativehidden32network29→32→32→16→d→norm.
- LegacyCEBRAlosses:Behaviorlast~5.04–5.085;Time~4.90–4.936. Lossdropdoesn'tprovepathinfo.

## Parent research sources for final HTML
Websearchresponse mtqqo2x9kztbyp(13/15fetched);fetchresponse **mtqqofy2a7i7t3**:
0 https://pmc.ncbi.nlm.nih.gov/articles/PMC5577566/ (Elsayed&Cunningham2017,10.1038/nn.4617,97kchars) parentreadfirst25k: populationgeometrycanfollowcondition/neuron/time means&covariance; source-labelnull testsassociation, notnovelcollectivegeometry; ourmomentidentityisNOTfullCFR/TMEreplication.
1 https://pmc.ncbi.nlm.nih.gov/articles/PMC3660664/ (MeyersNDT,60kchars) fetchedbutnotyetparentread.
2 https://readout.info/toolbox-design/datasources/basic_ds/ parentreadfull7.4k: supportsconditionmatchedpseudopops, preservegroupedrecordedneurons; trainpseudo/testsimultcontrolpossiblewhenrealpopulationavailable;nooverlaptrain/test. Thuspseudopopsaren'tuniversallyinvalid, butoursconditionalbenchmarknotoperationalrealtrial.
Varoquaux2018 DOI10.1016/j.neuroimage.2017.06.061 fromsearchabstract: smallsample CVuncertainty; doNOTapplyits±10% at100 orAarts80% numberasourdatasetpowercalculation.
Prior researcher primary-literature.md has Aarts/Truccolo/multisessionCEBRA/POYO/NDT2, verifyclaims beforefinalcitation; no universalminimumN.

## Additional parent findings/amendments AFTER initial manager note
- Parent behavior-only ranking of ALL24staticdirectedcomponents, TRAINsplitonly: for eachsession/E require>=3source/class, then sessionswith>=20eligibletraining sources. Rank bynumberofsuchsessions, then totaltrain sources. Best MIDDLE is D_N_C_M__N_C_B:49eligiblecontexts,11sessions>=20,267train sources. Originalmiddle=38contexts,5sessions>=20,134train sources. Originalanywhere=29contexts,4sessions>=20,108train sources. Candidate selectedBEFOREany new neuralperformance/fitting.
- User was told this is a better-supported real-trial design and we WILL TEST the oneadditionalcandidate, notneuraledgehunt. Worker76f17d7b instructed tofreezeprotocol amendment/selectiontable; add supported_middle target, coherentjointTHREE-labelsource permutations andmaxTHREEglobalstats forordinary+temporal nulls. KeepA/B unchanged. No otheredge orGPUmodelsadded. Same20/3eligibility andlambda1; cohorts maydiffer.
- Originalmiddle supportanythreshold:38contexts/30sessions;5sessions>=20 source counts22,23,24,31,34. Originalanywhere29contexts/22sessions;4sessions>=20 counts20,23,31,34. Below20isnotuniversalimpossibility, justprefitfloor; doNOTrelaxafterneuralresults.
- Othertrain-behavior rankings (notfit): anywhere topD_N_C_T__N_R_T supports14sessions369train; oppositeD_N_R_T__N_C_T supports13sessions390train. TheseNOTaddedasmodels. Bestmiddlechosenretainsoriginalshared-middlequestion.
- Directionquality: acrossV6allselectedoldEtraversals817=757middle+60nonmiddle, ALLdirection_source='adjacent_nodes'. NewcandidateD_N_C_M__N_C_B has1465traversals=1359middle+106nonmiddle, alsoALLadjacent_nodes. Noextra directionfilterneeded.
- Fullroute_signatures canbe noncontiguousinferrededge-token sequences:23/660selectedoldcondition (12present,11absent). DoNOTcallthemguaranteedcompletegraphwalks. Selectedbinarycomponentdirectionevidenceisstronger. No inferenceoftruncation/clockbug.
- Parent sentmatchedfinite-sampleRidge arm request: rawbinned lambda1, same4rows×20seeds vs exacttrain-Qridge. Logistic cannot be claimedtoconvergetoridge (differentloss). Naturalridgeprobabilitylinkclip((score+1)/2); otherwiseBA/AUC only. NoextraGPUfits.
- Auxiliaryattentionalertworker76f17d7b wasfalsepause; statusshowedactive2s. Lastinspectionworkerhad~36turns38tools,implementingfixes.
- Parent verifiedlegacycoefs exist inR/final.../v8b/coefs/seed0_raw_total_C1.npz etc; toldworkerafterwrongglobreturned[]; avoidunnecessaryrefitclaims.
- Parentreadtheoldfit_infoslosses (notnewfits):Behaviorlast~5.04–5.085, Time~4.90–4.936. Don'tassumeabsoluteCEBRAlossneedsapproachzero; objectiveiscontrastive, notpathCE.
- Interesting reportderivation (notbiologicalclaim): forIIDzero-signalunitvarianceGaussian sources withACTUAL primaryunequalpoolcounts, expectedwithin-Qcovtrace train~22.606,validation~6.667; expectedbetweenclassnoise trace train~3.197,validation~11.167. Derivecarefullybeforeusing. Smallvalpools shrinkwithinclassQvariance andinflateclass-meanestimationnoise evenifunderlyingbiologyunchanged. Gaussiancontrols canillustrate; no extra modelbudgetrequested.

## CURRENT EXECUTION STATUS (supersedes older closed-gate notes)

Gate APPROVED by independent frozen-execution-gate-review.md, reviewer c3dcd871 (completed,no findings). Parent took over implementation fixes; old worker76f17d7b ended with acceptance-format rejection criterion-1, not scientific/runtimefailure.

Frozen artifacts in newtree outputs/path-generalization-20260907/frozen/:
- driver.py SHA2821317f843ca2b285f2db20d9587c5dd594511e42b5fd63ad304130e4417de1 (read-only444), used forB/C.
- protocol.md SHA14e13571233b12727b7ab5e51022eddb6e379bfbe881ba83f405afcd6e14483b (same liveprefitdoc; nevereditduringfitting).
- driver_track_a_v2.py SHA340bd4fa14ee90b0a57cbc384785dff5be5936ab08146aee1e6620c0050d7bfb, differsONLYV9legacyCSVreader removesCfilter (CSVhasnoC). UsedsuccessfulA.
- Executewithcwdnewtree,PYTHONPATH=$PWD, OPENBLAS/OMP/MKLthreads1, PYTHONDONTWRITEBYTECODE1, oldisolatedruntime.
- RUN ROOT = outputs/path-generalization-20260907/results-20260907T081200Z. execution_gate.json and work/research-planning/ACTIVE_RUN.json containauthorization.

Parent criticalfixes beyondworker: relaxed40 trulyreal-sessionrows neverbuild_dataset +numerictrialindex +nestedsourcefractions; sourcebudgetmoment-exactridge avoidingMC, slicemetas/X/Mtogether; exactPCAconnected+matchedheads; source-IDcontrol filteredTRAINmanifest(previouslyleakedvalidationIDs intoidentityfeatures); strictnamedlabelnofallback;static24catalog/qualified267/134ranking; covarianceGaussianactualcelllayout andvectorizedMC;rawrankingAUCnotclipped; artifactreusehashes/allfiles/stepchecks andactualnumerical1000prefix; addtests scripts/test_place195_path_generalization_execution.py (9testsnow). 36combinedtestsplusCUDA2/4step syntheticprefix/reload0passed; extraCSVreaderregression1passed. 30testsindependentreviewpassed. FullsyntheticTrackAprogramsmoke33metricrows/4knowntruthcasespassed. No sourcefittingcodeedits now; runssnapshotimmutable.

ACTUAL completed data/experiments:
- Export task be0be36d1 completed8s. track_c_export/development_cue_counts.csv.gz:64051unit-trialrows,19162uniqueSourceIDs,195units. Hashb0f00cff980d0b813b638a3a2d51fff44e52809041957cd0af4bc817c16919d2. Originalmixedcuefile streamedONLYguarded,12486testrowsSKIPPED,zero forbiddenyield. Allsource/cell layoutrectangularwithinSession,nomissingallowlistsource. QC18sourcesglobally, butNONEinmodeledcohorts. data_gate_checks.json records.
- TrackCtask b94063d5c COMPLETED7m59s, root/track_c. All3targets ordinary100+temporal100 jointnulls. Sourcecohorts:middle15units/5sessions/134train/25val;anywhere12/4/108/22;supported_middle43/11/267/52. Predictionrows78/68/217—notindependenttrials. Independentreview work/research-planning/track-c-results-review.md nofindings;recalcLL≤3.33e-16, allnullcohortsignaturesinvariant and0jointlabelviolations.
  MeanΔLL baseline-minus-neural: middle−.0106805323,any+.00187799467,supported+.00386014348. Supported8/11sessionpointestimatespositivebutpordinary.0990099,temporal.1980198. Max3family pordinary.4752475,temporal.4356436. No convincingincrementalcue-rateevidence.
- FirstTrackAtask b54c17900 FAILED1m40duringlegacyV9CSVreaderKeyErrorC; coreoutputsretainedroot/track_a,DO NOTpool. No changedfits/labels/hyperparameters;patchedreaderonlyinnewv2snapshot. Failure+fix receipt root/track_a_reader_fix.json.
- ReplacementTrackAtask bf9a9d6d5 COMPLETED1m49, root/track_a_v2. 1847metricrows,55410predrows,1800knownGaussian cases,1980relaxed40real-sessioncontrols. Fullstagecompletion. OldpredparityV8b9.10e-8,V9Cebra8.67e-8. Independentreviewtrack-a-results-review.md onlyminor:replaytablesomitlegacydecoderiteration/Cmetadata, citeacceptedoriginalmetricsforit.
  ExactQ24abs/6pres. LegacyV9BAchanges≤.031;zero/constantcasesremainzero/.5. Momentexactridgeλ1BA.4791667,AUC.5069444. Matchedsampledridge rows16/64/256/1024meanBA.475/.48125/.480208/.480208;N1024range.47917–.5. Rawnormalizedlogisticbinnedmean.4802/.4823/.4885/.4885;notrescuedbypseudoN.
  Sourcebudget(.5,.75,1):meanBA.44375/.470833/.479167;halfsourcesrange.020833–.854167;fullsourceexactconstant. Four7blockscorecontrastsreverse (07/30,07/31,08/10,09/20). Leaveout08/10 improves.479→.8333;leaveout09/12lowers.3333. DiagnosticNOTvalidatedsessionselection.
  Gaussianzero-signaltrueBA/AUC=.5exactly,train3/val1perclass/session100seeds:30perfectempiricalQ,16inverse,mean.57 finiteMCnottrueimprovement. CovtraceD290observed47.893vsexpected48.333(n3),14.293vs14.5(n10),4.83vs4.833(n30). Coordinate noiseindependenceisTOYassumption.

ACTIVE MAIN GPU JOB:
- **b051be988** `Run CEBRA ablations nulls`, PID2792499, root/track_b. StartedafterA2completed. Commandfrozen/driver.py run-track-b --authorized-phase reviewed-code-data-gate --null-permutations20 --output-dirRUN/track_b. timeout4h,triggerOnCompletionfalse. Mustcheckbg_status thenlogs; thenfinal342fits/510000updates/42prefixpairs beforeclaims.
- Lastprogress89completedfitreceipts:50crossed+12sensitivity+27null. Median1000fit9s,5000fit45s; total~75min expected. No otherGPUjobours; Cdone.
- All62observedalreadycomplete. 5x5exactvalmeans:Time.2491667(range0–.5),Behavior.3516667(.0833–.625). DescriptivegridSSsharesA/O/interaction:Time.165129/.071597/.763274;Behavior.244286/.203549/.552165.
- A0O0observed14maxBA=.5833333. Time d3/8/16/29 BA=.4375/.4167/.1667/.1667;Behavior=.5833/.5/.5208/.5. Rows64/256/1024 Time=.4167/0/.2083,Behavior=.5/.2708/.1667. 5000updatesTime8BA.3333,Behavior8BA.5833. Fullnullp STILL PENDING,donotusepartialnulls.

COMPLETED extra predeclared CPU replay:
- New script scripts/replay_path_generalization_assemblies.py SHAc7c69eb1df97a9760b327402a6047abeb92afb487c55781046d7dab2e1b078d4. Read-only50checkpointreplay,nonewfitting;reconstruct5Atrainingarraysandverifytheirhashagainstfits. Parentinitialattempt b48bb919e failedassumptionfirst50receiptsallfactorial (sensitivityfitsinterleave);fixedROLEfilter,notmodelissue.
- Correcttask bc053959e COMPLETED6s, output RUN/assembly_transfer/{assembly_transfer_metrics.csv,replay_parity.csv,summary.json}. 250rows =50own+200otherA. CPUGPUmaxembeddingdiff1.131743e-5,prob5.02862e-7;ownlabelsagree.
- OwntrainBA1all50;newmixturesSAMEtrainingsources Time mean.9925range.96094–1,Behavior.99765625range.97656–1. VersuspoorSOURCE-DISJOINTexactvalabove. Locatesfailureacrosssourcesnotmerely64specificcombinations;stillNOTindependentbiologicalvalidation.

CURRENT REPORT WRITER (SOLE code/report writer now):
- **b1beed28-f52c-4f09-b2f3-b8d00913a4e2**, workerfresh, draftingreport/assetswhileBnullsrunning. ParentMUSTNOTedititsfileswhileactive.
- Allowedwrites NEWscripts/build_path_generalization_report.py, RUN/report_assets/*,work/report-draft/*,ownhandoff. Noanalysis/modeldatachanges,fits,rawaccess,installs,commits,services.
- DRAFTphaseonly. Finaltarget docs/professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.html. RequireBcompleteforfinal; draftlabelifpending. ParentwillresumeafterBdoneandthenindependentpedagogy/factualreviewandbrowserrender.
- Writerhasfullteaching-firstinstructions (~6000–9000usefulwords),actualA/C/observedB/crossAfigures+proofs+failures/claimlimits,8–12realgraphs, scriptsnoforeignassets andsingleHTMLoffline. FinalBnullmustwait. Outputhandoff work/research-planning/report-draft-handoff.md.
- Nativefit/allmodelsourcecodeMUSTremainimmutable. Onlyreportcodewriteractive;parentcanread/arithmetic/review butnoeditsnewworktreesourceconcurrently.

## Latest status / finalization (after draft received)
- TrackA andC read-onlyreviewscompleted. Aonlyminor missinglegacyC/decoderiterationmetadata inreplaytables—citeoriginalacceptedmetrics. Cno findings,recalculatedΔLLmatches≤3.33e-16;100ordinary+100temporalnulls400rowseach(3targets+familymax),allcohortsignaturesmatchand0labelimplicationviolations.
- Crossassemblyreview2b69a859completed nofindings;scopeCPUforward50checkpoints,250metrics,nonewfits,sourcehashes/parity/meansconfirmed. Review work/research-planning/assembly-transfer-review.md.
- B bgjob b051be988 wasstillRUNNING at1h16elapsed;lastcount earlier250/342,362000/510000updates. Expected~75–80min. Needcheckterminalstatusthenreadsummary/prefix/familymax. No fullBnullresultyetinthismanagerentry.
- Reportwriterb1beed28completed DRAFT. Draftwork/report-draft/path-generalization-teaching-audit-20260907-draft.html (~6014words,12inlineSVGs). Generator scripts/build_path_generalization_report.py. It mistakenlyusedLITERALnewtree/R/report_assets/path_generalization_20260907 (Rwasalias) andfinalmodehardcodedDRAFT/pending; parentreadgenerator/fullproseandfoundotherpedagogy/provenancegaps.
- Writerresumed/current **59651bbc** tofixandfinalizeonlyafterparentconfirmsBcomplete. SOLEreportwriter, noanalysiscodechanges. Task12fixes:moveownliteralRassetsintorealRUN/report_assets;properfinalguard requiresBsummarycomplete342+42numericprefixchecks notjust280fitfiles; replacehardcodedDraft/pendinginfinal;objective/measurementBEFOREperformance;middlemeansALLinteriorruns excludingfirst/last,notone'slot';noactualsourceleakclaim(finalvaldisjoint,source-IDcontrolbugfixedprefit); CoperationalPERUNITinputconstructionnotpseudo;properprobmetricsaren'tcalibration-only;Gaussiantraceassumptionszeroδ+IIDsource;addfull62Btable/20nullmax/Acompactsummary/C70modelrows/code/protocol/inputhashes+timings;concretenextprojectgatesnotgenericmoredata;A4printCSS;prefixSVGidsandrefs/accessibility;keepfixedgridvariance/familymaxscopeprecise.
- Parentshouldnoteditreportfileswhile59651bbcactive. Bsourcecodeimmutable andCcomplete. Parentcanread/checknumericoutputs.
- NeedindependentfinalBscientific/numericreviewandfinalHTMLpedagogy/factualreview,thenChromeheadlessdesktop/A4render+inspect.

## FINAL B DONE — authoritative numerical correction
- B task b051be988 COMPLETED exit0, wall1:18:29,342fits,684metricrows,42prefixpairs. FrozenBdriver2821 unchanged.
- Rawproducerfamilymaxp=.857142857 (17exceedances) hadFLOAT-TIE bug: null19=.5833333333333333 ismathematicallysame7/12 asobserved .5833333333333334. Parentcaughtafterfits; no models/predictionschanged.
- Parent audit bg badceb96f COMPLETED5s. RUN/audits/track_b_exact_audit.json +track_b_exact_ba.csv areAUTHORITATIVE corrected inference. RecomputedBA asFraction(correct_abs/48+correct_pres/12) fromall342savedvalidationdecisions,assert24abs6presweights. 18/20nullmaxima>=obs7/12; p=19/21=.9047619048. Sevenof20nullsperfect1. Botholdrawreceiptandcorrectionpreserved.
- Auditverifiedall4488artifacthashes,510000lossrows,allCUDA/nonzeroalloc,allproducerreload0,alltrain/evalsourceIDsdisjoint,all42numerical1000prefixweight/lossdifferences0. Nullmaxfractionsper0..19:1,1,2/3,41/48,3/4,7/8,1,15/16,31/48,5/6,7/12,7/12,1,1,13/16,1/2,1/2,1,1,7/12.
- IndependentFINAL B reviewer **39f008d7** currentlyreadingthiscorrection/results; outputwork/research-planning/track-b-final-review.md. No newfits.
- Reportwriter59651bbc wasnotifiedBcomplete+correctedreceipt; maynowgenerateFINAL-readyHTMLafterrequestedfixes. Mustusecorrectedp.9048, explainraw.857 float-tie correction. Parentwillstillpedagogy/factualreview+renderbeforeuserdelivery.
- Allstudyfittingjobs nowdone. Onlyreportwriter/revieweractive; oldpreviewHTTPservermaystillrun, don'tclaimalljobsstoppedwithoutchecking.
- FUTURE CODE NOTE: live analysis `_p_value_greater_equal` stillstrictfloat>= inretainedfrozen code. Afterreportwriterhandsback(parentsolewriter), consider minimaldocumentednumeric-tie handling+regressiontest inLIVEsource only; NEVEReditfrozenmodelproducer/artifacts. CurrentreportusesexactFractionaudit,so no refitneeded. Also savea runnableoutputverification script iftimeallows,parentauditwasinlineBashscriptretainedlogs.

## Next steps (UPDATED)
1. MonitorB b051be988 throughbg_status/logs, nohotpoll. Awaitreportwriterb1beed28 via subagent_wait ifneeded(run-to-completionrequest). No furthermodel/targetexpansion.
2. WhenBcompletes, readsummary/familymaxp/prefixmetrics andindependentlyaudit342fitrecords510000lossrows,identity/inputsourcealignment/exactweights/42pairedprefixes. Getfreshread-onlyscientificreview.
3. Read/reportwriterdraft,finishfullresultsafterBcompletion(resumewriter);ensuregraphsactualnotphase1smoke,andallscopes/meansconsistent. Parentpersonallyreviewsexplanationbeforeoutcomes.
4. IndependentreviewHTMLpedagogy+numeric/provenance,fixasonewriter,renderdesktop/A4withinstalledGoogleChrome isolatedtempprofile(noinstall). PortableHTMLCSS+SVG+base64imagesnoJS/noautoloadremote.
5. Deliverreportlink/file,newworktree/branch,keyfindingsandconcreteresearchdirection,notpositivebiooverclaim. No commits/pushasked. Preserveoriginaldirtybaseline.
6. Updatefinalstate/READMEpointerinNEWtreeonly. ExistingoldHTTP8765maystillserve/tmp/pi-teach;checkbeforenewserver. cmuxrelay53167oftenfails;don'tclaimbrowseropenedifnot.

## Earlier next-step notes (historical)
1. Wait/inspect currentwriter76f17d7b; no biologicalapprovaluntil criticalfixes/endtoendsmokescomplete.
2. Independentlyre-reviewupdatedimplementation(bothABandC), parentreadbodies, primaryLSP+tests. Resolveblockers withsolewriter.
3. Authorize actualrunsthenrun tocompletion (likely1–2h), oneGPUjob; saveoutputs/logs,inspectstatusbeforelogs. Tests/buildslongusebg_run. Scientificworkers mustawaitownedbgjobsbeforefinalhandoff.
4. Parentmayreadresearch/prepareanalysiswhileworkerexecutesbutnotedititscode concurrently. Needadditionalpostresultscientificaudit andnumericalchecks.
5. Build teaching-firstself-containedprofessorHTML innewworktree, ownrealfigures plusexplicitlylabelledknowntruthsimulationgraphs. Objectiveandmeasurement BEFOREoutcomes, perhypothesislogic/verdict, fulltables/provenance/attempts, exactmathclaimsstatedwithassumptions, noforcedpositivebiology. Correctpriorabsencelabelshorthand prominently.
6. Deliverfile/worktree/branch, keyfindings andconcrete nextresearchdesign. No commits/pushasked. Preserveoriginaldirtyfile.
7. Existingoldpreviewservermaystillserve/tmp/pi-teach port8765; checkbeforestartingduplicates. Reuseonlyloopbackandservejustreportdirectoryifneeded; oldcmuxautoopenrelay53167oftenfails, don'tclaimsuccess. Finalreportofflineportable.
