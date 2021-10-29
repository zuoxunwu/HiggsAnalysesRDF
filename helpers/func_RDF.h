#include "ROOT/RDataFrame.hxx"
#include "ROOT/RVec.hxx"
#include "Math/Vector4D.h"
#include <vector>

using namespace ROOT::VecOps;
//using RNode = ROOT::RDF::RNode;
using rvec_f = const RVec<float> &;
using rvec_i = const RVec<int> &;
using rvec_b = const RVec<int> &;

template <typename T>
RVec<T> vec4_pz(const RVec<T>& pt, const RVec<T>& eta, const RVec<T>& phi, const RVec<T>& mass) {
    using size_type = typename RVec<T>::size_type;
    const size_type s = pt.size();
    auto pz = RVec<T>(s);
    for (size_type i = 0; i < s; i++) {
        ROOT::Math::PtEtaPhiMVector vec4(pt[i], eta[i], phi[i], mass[i]);
        pz[i] = vec4.Pz();
    }
    return pz;
}

template <typename T>
T sum_vec4_pt(const RVec<T>& pt, const RVec<T>& eta, const RVec<T>& phi, const RVec<T>& mass) {
    using size_type = typename RVec<T>::size_type;
    const size_type s = pt.size();
    ROOT::Math::PtEtaPhiMVector vec4_total(0, 0, 0, 0);
    for (size_type i = 0; i < s; i++) {
        ROOT::Math::PtEtaPhiMVector vec4_this(pt[i], eta[i], phi[i], mass[i]);
        vec4_total += vec4_this;
    }
    return vec4_total.Pt();
}

template <typename T>
T sum_vec4_pz(const RVec<T>& pt, const RVec<T>& eta, const RVec<T>& phi, const RVec<T>& mass) {
    using size_type = typename RVec<T>::size_type;
    const size_type s = pt.size();
    ROOT::Math::PtEtaPhiMVector vec4_total(0, 0, 0, 0);
    for (size_type i = 0; i < s; i++) {
        ROOT::Math::PtEtaPhiMVector vec4_this(pt[i], eta[i], phi[i], mass[i]);
        vec4_total += vec4_this;
    }
    return vec4_total.Pz();
}

template <typename T>
T sum_vec4_phi(const RVec<T>& pt, const RVec<T>& eta, const RVec<T>& phi, const RVec<T>& mass) {
    using size_type = typename RVec<T>::size_type;
    const size_type s = pt.size();
    ROOT::Math::PtEtaPhiMVector vec4_total(0, 0, 0, 0);
    for (size_type i = 0; i < s; i++) {
        ROOT::Math::PtEtaPhiMVector vec4_this(pt[i], eta[i], phi[i], mass[i]);
        vec4_total += vec4_this;
    }
    return vec4_total.Phi();
}
