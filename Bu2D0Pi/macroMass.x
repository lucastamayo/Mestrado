{
    TChain* events = new TChain("events","events");
    events->Add("./analysis/p8_ee_Zbb_ecm91_EvtGen_Bu2D0Pi.root");

    // Cria um canvas único
    TCanvas* c = new TCanvas("c", "Mass Distributions", 1200, 600);

    // Configuração para os histogramas e o TLatex
    gStyle->SetOptStat(1111);   // Entries only
    TLatex tt;
    tt.SetTextSize(0.04);

    // Cria histogramas para armazenar a massa invariante e a massa de Monte Carlo
    TH1F* h_mass_D0 = new TH1F("h_mass_D0", " ;D^{0} Invariant Mass (GeV/c^2);Number of Events", 100, 1.8, 1.9);
    TH1F* h_mass_MC = new TH1F("h_mass_MC", " ;D^{0} Invariant Mass (GeV/c^2);Number of Events", 100, 1.8, 1.9);

    // Define as cores dos histogramas
    h_mass_D0->SetLineColor(kBlue);
    h_mass_MC->SetLineColor(kRed);

    TLorentzVector* LorentzD0 = nullptr;
    ROOT::VecOps::RVec<float>* D0MCMass = nullptr; 
    events->SetBranchAddress("LorentzD0", &LorentzD0);
    events->SetBranchAddress("D0MCMass", &D0MCMass);

Long64_t nentries = events->GetEntries();
for (Long64_t i = 0; i < nentries; ++i) {
    events->GetEntry(i);

    // Preenche o histograma com os valores de massa de Monte Carlo
    for (auto& mass : *D0MCMass) {
        h_mass_MC->Fill(mass);
    }

    // Calcula a massa invariante para o evento e preenche o outro histograma
    Double_t mass2 = LorentzD0->M(); 
    h_mass_D0->Fill(mass2);
}
    // Desenha os histogramas no mesmo canvas
    h_mass_D0->Draw();
    h_mass_MC->Draw("SAME"); // Desenha este histograma no mesmo canvas sem apagar o anterior

    // Adiciona uma legenda para diferenciar os histogramas
    TLegend* leg = new TLegend(0.1,0.7,0.3,0.9);
    leg->AddEntry(h_mass_D0, "Reconstructed Mass", "l");
    leg->AddEntry(h_mass_MC, "Monte Carlo Mass", "l");
    leg->Draw();

    // Salva o gráfico em um arquivo
    c->SaveAs("distribuicao_massa_d0_comparacao.png");
}
