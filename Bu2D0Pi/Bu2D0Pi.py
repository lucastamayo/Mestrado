#Optional test file
#testFile="/eos/experiment/fcc/ee/generation/DelphesEvents/winter2023/IDEA/p8_ee_Zbb_ecm91_EvtGen_Bu2D0Pi/events_042861215.root"
#testFile="/eos/user/l/lmonteta/million.root"
import ROOT


processList = {
    'p8_ee_Zbb_ecm91_EvtGen_Bu2D0Pi':{},
}


#Mandatory: Production tag when running over EDM4Hep centrally produced events, this points to the yaml files for getting sample statistics
prodTag     = "FCCee/winter2023/IDEA/"

nCPUS       = 4
runBatch    = False

outputDir    = "./analysis"

#Function that returns the TLorentzVector of a RecoParticle in the format (Px, Py, Pz, E)
get_tlv_code='''
#include "FCCAnalyses/ReconstructedParticle.h"

TLorentzVector get_tlv2(edm4hep::ReconstructedParticleData in) {
  TLorentzVector result;
  result.SetPxPyPzE(in.momentum.x, in.momentum.y, in.momentum.z, in.energy);
  return result;
}



'''


ROOT.gInterpreter.Declare(get_tlv_code)


#Mandatory: RDFanalysis class where the use defines the operations on the TTree
class RDFanalysis():

    #__________________________________________________________
    #Mandatory: analysers funtion to define the analysers to process, please make sure you return the last dataframe, in this example it is df2
    def analysers(df):
        df2 = (
            df

               .Alias("Particle1", "Particle#1.index")
               .Alias("MCRecoAssociations0", "MCRecoAssociations#0.index")
               .Alias("MCRecoAssociations1", "MCRecoAssociations#1.index")

               # ---------------------------------------------------------------------------------------
	       #
               # -----  Retrieve the indices of the MC Particles of interest

               # MC indices of the decay B+(PDG = 521) -> D0 (PDG = -421) Pi+ (PDG = 211) 
               # Retrieves a vector of int's which correspond to indices in the Particle block
               # vector[0] = the mother, and then the daughters in the order specified, i.e. here
               #       [1] = the D0, [2] = the Pi
               # Boolean arguments :
               #	1st: stableDaughters. when set to true, the daughters specified in the list are looked
               #             for among the final, stable particles that come out from the mother, i.e. the decay tree is
               #             explored recursively if needed.
               #        2nd: chargeConjugateMother
               #        3rd: chargeConjugateDaughters
               #        4th: inclusiveDecay: when set to false, if a mother is found, that decays
               #             into the particles specified in the list plus other particle(s), this decay is not selected.
               # If the event contains more than one such decays,only the first one is kept.
               .Define("Bu2D0pi_indices", "MCParticle::get_indices( 521, {-421, 211}, false, false, false, false) ( Particle, Particle1)" )
               # select events for which the requested decay chain has been found:
               .Filter("Bu2D0pi_indices.size() > 0")

               .Define("Bu_MCindex",  "return Bu2D0pi_indices[0] ;" )
               .Define("D0_MCindex",  "return Bu2D0pi_indices[1] ;" )
               .Define("Bachelorpi_MCindex",  "return Bu2D0pi_indices[2] ;" )


               # MC indices of (this) D0 -> K Pi
               # Boolean arguments :
               #        1st: stableDaughters. when set to true, the daughters specified in the list are looked
               #             for among the final, stable particles that come out from the mother, i.e. the decay tree is
               #             explored recursively if needed.
               #        2nd: chargeConjugateDaughters
               #        3rd: inclusiveDecay
               .Define("D02KPi_indices",  "MCParticle::get_indices_MotherByIndex( D0_MCindex, { 321,  -211 }, false, false, false, Particle, Particle1 )")
               .Filter("D02KPi_indices.size() > 0")
               .Define("Kplus_MCindex",  "return D02KPi_indices[1] ; ")
               .Define("Piminus_MCindex",  "return D02KPi_indices[2] ; ")

               # ---------------------------------------------------------------------------------------


               # ---------------------------------------------------------------------------------------
               # -----    The MC Particles :

               # the MC Bu :
               .Define("Bu",  "return Particle[ Bu_MCindex ]; ")
               # the MC D0:
               .Define("D0",  "return Particle[ D0_MCindex ]; ")
               # the MC bachelor Pi+ from the Bu decay :
               .Define("Bachelorpi",  "return Particle[ Bachelorpi_MCindex  ]; " )
               # The MC legs from the D0 decay
               .Define("Kplus", "return Particle[ Kplus_MCindex ] ; ")
               .Define("Piminus", "return Particle[ Piminus_MCindex ] ; ")

               # some MC-truth kinematic quantities:
               .Define("Bachelorpi_px", "return Bachelorpi.momentum.x ;")
               .Define("Bachelorpi_py", "return Bachelorpi.momentum.y ;")
               .Define("Bachelorpi_pz", "return Bachelorpi.momentum.z ;")

               .Define("D0_px",  "return D0.momentum.x ;")
               .Define("D0_py",  "return D0.momentum.y ;")
               .Define("D0_pz",  "return D0.momentum.z ;")
               .Define("D0_E", "ROOT::VecOps::RVec<edm4hep::MCParticleData> v; v.push_back( D0 ); return MCParticle::get_e(v ) ;")
               .Define("D0MCMass", "sqrt(D0_E*D0_E - D0_px*D0_px - D0_py*D0_py - D0_pz*D0_pz);")
               .Define("D0_pt", "ROOT::VecOps::RVec<edm4hep::MCParticleData> v; v.push_back( D0 ); return MCParticle::get_pt(v ) ;")
               

               .Define("Bu_px",  "return Bu.momentum.x ;")
               .Define("Bu_py",  "return Bu.momentum.y ;")
               .Define("Bu_pz",  "return Bu.momentum.z ;")
               .Define("Bu_E", "ROOT::VecOps::RVec<edm4hep::MCParticleData> v; v.push_back( Bu ); return MCParticle::get_e(v ) ;")
               .Define("BuMCMass", "sqrt(Bu_E*Bu_E - Bu_px*Bu_px - Bu_py*Bu_py - Bu_pz*Bu_pz);")
               .Define("Bu_pt", "ROOT::VecOps::RVec<edm4hep::MCParticleData> v; v.push_back( Bu ); return MCParticle::get_pt(v ) ;")
               
               # ---------------------------------------------------------------------------------------


               # ---------------------------------------------------------------------------------------
               # -----    The RecoParticles that are MC-matched with the particles of the Ds decay

               # RecoParticles associated with the Ds decay
               # Note: the size of D0RecoParticles below is always 3 provided that D02KPi_indices is not empty.
               # possibly including "dummy" particles in case one of the legs did not make a RecoParticle
               # (e.g. because it is outside the tracker acceptance).
               # This is done on purpose, in order to maintain the mapping with the indices - i.e. the 1st particle in
               # the list BsRecoParticles is the Kminus, then the Kplus, then the Piplus.
               # (selRP_matched_to_list ignores the unstable MC particles that are in the input list of indices
               # hence the mother particle, which is the [0] element of the Ds2KKPi_indices vector).
               #
               # The matching between RecoParticles and MCParticles requires 4 collections. For more
               # detail, see https://github.com/HEP-FCC/FCCAnalyses/tree/master/examples/basics

               .Define("D0RecoParticles",   " ReconstructedParticle2MC::selRP_matched_to_list( D02KPi_indices, MCRecoAssociations0,MCRecoAssociations1,ReconstructedParticles,Particle)")
               
               .Define("RecoK",  " return D0RecoParticles[0] ; ")

               .Define("RecoPi",  " return D0RecoParticles[1] ; ")

                #Return the TLorentzVector of RecoPi
               .Define("LorentzRecoPi",  " get_tlv2(RecoPi) ; ")
                #First Element of TLorentzVector (p_x)
               .Define("RecoPiPx",  " LorentzRecoPi[1] ; ")
                #Return TLorentzVector of Reco K
               .Define("LorentzRecoK",  " get_tlv2(RecoK) ; ")
               .Define("RecoKMass", "LorentzRecoK[3]")
               .Define("RecoPiMass", "LorentzRecoPi[3]")


                #Reconstructed Lorentz Vector of D0
               .Define("LorentzD0", "LorentzRecoPi + LorentzRecoK")
                
                #D0 Energy
               .Define("D0E", "LorentzD0[3]")

                #Invariant Mass of D0
                .Define("MassD0", "sqrt(LorentzD0[3]*LorentzD0[3] - LorentzD0[0]*LorentzD0[0] - LorentzD0[1]*LorentzD0[1] - LorentzD0[2]*LorentzD0[2]);")

                #Define Bu decays particles
                .Define("BuRecoParticles",   " ReconstructedParticle2MC::selRP_matched_to_list( Bu2D0pi_indices, MCRecoAssociations0,MCRecoAssociations1,ReconstructedParticles,Particle)")
                #Select Reconstructed Bachelor Pi
                .Define("RecoBachelorPi", " return BuRecoParticles[0] ; ")
                #TLorentz Vector of Reco Bachelor Pi
                .Define("LorentzRecoBachelorPi",  "get_tlv2(RecoBachelorPi) ; ")
                #TLorentz Vector of Bu
                .Define("LorentzBu", " LorentzRecoBachelorPi + LorentzD0 ;")
                #Invariant Mass of Bu meson
                .Define("MassBu", "sqrt(LorentzBu[3]*LorentzBu[3] - LorentzBu[0]*LorentzBu[0] - LorentzBu[1]*LorentzBu[1] - LorentzBu[2]*LorentzBu[2]);")
        )
        return df2


    #__________________________________________________________
    #Mandatory: output function, please make sure you return the branchlist as a python list
    def output():
        branchList = [
                "Bachelorpi_px", "D0_px", 
                "LorentzRecoPi", "LorentzRecoK", 
                "LorentzD0", "RecoPiPx", "D0E", 
                "MassD0", "MassBu", 
                "LorentzBu", "D0MCMass", "D0_pt",
                "Bu_px", "Bu_py", "Bu_pz",
                "Bu_E", "BuMCMass", "Bu_pt", "RecoPiMass", "RecoKMass"

        ]
        return branchList
